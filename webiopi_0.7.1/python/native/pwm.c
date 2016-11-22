/*
Copyright (c) 2016 Thor Watanabe

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include "gpio.h"
#include "cpuinfo.h"
#include "pwm.h"
#include <syslog.h>

/*
Rereferences:
  [1] BCM2835 Peripheral specification: 
      https://www.raspberrypi.org/wp-content/uploads/2012/02/BCM2835-ARM-Peripherals.pdf
      pp. 102-108 for clock manager, pp. 138-146 for PWM.
  [2] BCM2835 Errata: 
      http://elinux.org/BCM2835_datasheet_errata
  [3] BCM2835 DTS: 
      http://lxr.free-electrons.com/source/arch/arm/boot/dts/bcm283x.dtsi
  [4] Linux Kernel BCM2835 PWM Driver: 
     http://lxr.free-electrons.com/source/drivers/pwm/pwm-bcm2835.c
  [5] Linux Kernel BCM2835 CPRMAN Driver:
      http://lxr.free-electrons.com/source/drivers/clk/bcm/clk-bcm2835.c
*/

const static int g_wip_cm_clk_table[WIP_CM_SIZE_CLK_SRC] = {
  0,         // 0
  19200000,  // 1
  0,         // 2
  0,         // 3
  650000000, // 4
  200000000, // 5
  500000000, // 6
  216000000  // 7
} ;

const char g_wip_cm_clk_name[WIP_CM_SIZE_CLK_SRC][8] = {
  "",      // 0
  "osc",   // 1
  "",      // 2
  "",      // 3
  "plla",  // 4
  "pllc",  // 5
  "plld",  // 6
  "pllh"   // 7
};

// Maximum operating frequency of PWM clock at 1.2V:
#define WIP_CM_MAX_FREQ (25 * 1000 * 1000) // 25 MHz

// global variables 
static volatile uint32_t *wip_pwm_map = (uint32_t *)-1;
static volatile uint32_t *wip_clk_map = (uint32_t *)-1;

//thor
static volatile uint8_t *wip_clk_mem_orig = NULL;
static volatile uint8_t *wip_pwm_mem_orig = NULL;

// ----------------------------------------------------------------------
// Clock Manager 
// 
// two independent PWM channels shares a common pwm_clk.
// 
//          +-> pwm_sync_1 <-> pwm_chn_1 -> ch#1 (GPIO port 12 or 18)
//          |
// pwm_clk -+
//          |
//          +-> pwm_sync_2 <-> pwm_chn_2 -> ch#2 (GPIO port 13 or 19)

// Common Password 
#define WIP_CM_BIT_PASSWD  0x5a000000

// Clock Manager Register Address Offset
#define WIP_CM_ADR_OFFSET  0x00101000

// ------------------------------
// Registers

// PWM Clock Control 
#define WIP_CM_REG_PWM_CTL 0x000000a0
  #define WIP_CM_SFT_MASH 9          // MASH control
    #define WIP_CM_MSK_MASH0 0 // integer division
    #define WIP_CM_MSK_MASH1 1 // 1-stage MASH
    #define WIP_CM_MSK_MASH2 2 // 2-stage MASH
    #define WIP_CM_MSK_MASH3 3 // 3-stage MASH
  #define WIP_CM_MSK_BUSY (1 << 7)   // Clock generator is running
  #define WIP_CM_MSK_KILL (1 << 5)   // Kill the clock generator
  #define WIP_CM_MSK_ENAB (1 << 4 ) // Enable the clock generator
  #define WIP_CM_MSK_CSRC 0x0000000f // Clock source mask

// PWM Clock Divisors
#define WIP_CM_REG_PWM_DIV 0x000000a4
  #define WIP_CM_MSK_DIV  0x00000FFF // integer par of divisor
  #define WIP_CM_SFT_DIV  12         // integer par of divisor
  #define WIP_CM_MSK_DIVF 0x00000FFF // fractional part of divisor 

// ----------------------------------------------------------------------
// PWM

// PWM Reigster Address Offset
#define WIP_PWM_ADR_OFFSET 0x0020c000

// ------------------------------
// Registers

// PWM Control
#define WIP_PWM_REG_CTL    0x00
  #define WIP_PWM_CTL_SFT  8 // Ch2 Offset shift
  #define WIP_PWM_MSK_CH   0x000000FF // Ch mask
  #define WIP_PWM_MSK_MSEN (1 << 7) // M/S Enable
//#define WIP_PWM_MSK_CLRF (1 << 6) // Clear Fifo
//#define WIP_PWM_MSK_USEF (1 << 5) // Use Fifo
  #define WIP_PWM_MSK_POLA (1 << 4) // Polarity
//#define WIP_PWM_MSK_SBIT (1 << 3) // Silence Bit
//#define WIP_PWM_MSK_RPTL (1 << 2) // Repeat Last Data
//#define WIP_PWM_MSK_MODE (1 << 1) // Serialiser mode
  #define WIP_PWM_MSK_PWEN (1 << 0) // Channel Enable

#define WIP_PWM_REG_STA    0x04 // PWM Status 
//#define WIP_PWM_REG_DMAC   0x08 // PWM DMA Configuration
#define WIP_PWM_REG_RNG1   0x10 // PWM Ch1 Range (period)
#define WIP_PWM_REG_DAT1   0x14 // PWM Ch1 Data (duty)
//#define WIP_PWM_REG_FIF1   0x18 // PWM FIFO Input
#define WIP_PWM_REG_OFFSET 0x10 // Ch2 Register Offset

typedef struct _gpio_pwm_map_table_t {
  int gpio_port;
  int pwm_ch;
  int phy_port;
  int alt_func;
  int rpi_rev;
  int pullupdn;
} wip_pwm_map_table_t;

#define WIP_PWM_GPIO_PORTS 4
const wip_pwm_map_table_t wip_pwm_map_table[WIP_PWM_GPIO_PORTS] = {
  {12, 0, 32, ALT0, 3, PUD_DOWN},
  {13, 1, 33, ALT0, 3, PUD_DOWN},
  {18, 0, 12, ALT5, 0, PUD_DOWN},
  {19, 1, 35, ALT5, 3, PUD_DOWN}
};


// --------------------------------------------------
// prototype definitions
// 
static void wip_reg_write(volatile uint32_t *ptr, int reg, uint32_t value);
static uint32_t wip_reg_read(volatile uint32_t *ptr, int reg);
//
// CM
//
static int wip_cm_check_freq_range(float freq, int clk_src);
static float wip_cm_calc_divisor(float freq, int clk_src);
static inline int wip_cm_calc_divi(float div);
static int wip_cm_calc_divf(float div);
//
// PWM
//
// ns
int wip_pwm_set_period_ns(int ch, uint32_t period);
int wip_pwm_set_duty_ns(int ch, uint32_t duty);
// validator
static inline int wip_pwm_validate_map(volatile uint32_t *ptr);

// --------------------------------------------------
// function declarations

int wip_pwm_setup(int mem_fd)
{
  int ret = 0; 
  uint32_t clk_base = WIP_CM_ADR_OFFSET;
  uint32_t pwm_base = WIP_PWM_ADR_OFFSET;
  uint8_t *wip_clk_mem = NULL;
  uint8_t *wip_pwm_mem = NULL;

  syslog(LOG_INFO, "Initializing PWM features...");
  int rev = get_rpi_revision();

  if (rev > 2) {
    pwm_base += BCM2709_PERI_BASE_DEFAULT;
    clk_base += BCM2709_PERI_BASE_DEFAULT;
  } else {
    pwm_base += BCM2708_PERI_BASE_DEFAULT;
    clk_base += BCM2708_PERI_BASE_DEFAULT;
  }

  if ((wip_pwm_mem = malloc(BLOCK_SIZE + (PAGE_SIZE-1))) == NULL) {
    return SETUP_MALLOC_FAIL;
  }
  wip_pwm_mem_orig = wip_pwm_mem;
  

  if ((uint32_t)wip_pwm_mem % PAGE_SIZE) {
    wip_pwm_mem += PAGE_SIZE - ((uint32_t)wip_pwm_mem % PAGE_SIZE);
  }
  wip_pwm_map = (uint32_t *)mmap((caddr_t)wip_pwm_mem, BLOCK_SIZE, 
				 PROT_READ | PROT_WRITE, 
				 MAP_SHARED|MAP_FIXED, mem_fd, pwm_base);
  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    ret = -1;
    goto cleanup;
  }

  if ((wip_clk_mem = malloc(BLOCK_SIZE + (PAGE_SIZE-1))) == NULL) {
    ret = -2;
    goto cleanup;
  }
  wip_clk_mem_orig = wip_clk_mem;

  if ((uint32_t)wip_clk_mem % PAGE_SIZE) {
    wip_clk_mem += PAGE_SIZE - ((uint32_t)wip_clk_mem % PAGE_SIZE);
  }
  wip_clk_map = (uint32_t *)mmap((caddr_t)wip_clk_mem, BLOCK_SIZE, 
				 PROT_READ | PROT_WRITE, 
				 MAP_SHARED|MAP_FIXED, mem_fd, clk_base);
  if (wip_pwm_validate_map(wip_clk_map) < 0) {
    ret = -3;
    goto cleanup;
  }

  syslog(LOG_INFO, "Finished setting up PWM features.");
  return 0;
  
 cleanup:
  if (wip_pwm_validate_map(wip_pwm_map) >= 0) {
    munmap((void *)wip_pwm_map, BLOCK_SIZE);
    wip_pwm_map = (uint32_t *)-1;
  }

  if (wip_pwm_validate_map(wip_clk_map) >= 0) {
    munmap((void *)wip_clk_map, BLOCK_SIZE);
    wip_clk_map = (uint32_t *)-1;
  }

  return ret;
}

int wip_pwm_cleanup(void)
{
  syslog(LOG_INFO, "Cleaning up PWM featrures...");

  // disable all PWM channels
  if (wip_pwm_validate_map(wip_pwm_map) >= 0) {
    uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);
    value &= ~(WIP_PWM_MSK_CH << (0 * WIP_PWM_CTL_SFT));
    value &= ~(WIP_PWM_MSK_CH << (1 * WIP_PWM_CTL_SFT));
    wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, value);
  }

  // disable pwm_clk
  if (wip_pwm_validate_map(wip_clk_map) >= 0) {
    uint32_t val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);
    val &= ~(WIP_CM_MSK_KILL | WIP_CM_MSK_ENAB);
    val |= WIP_CM_BIT_PASSWD;
    wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_CTL, val);     
  }

  // unmap pwm/clk memory area
  if (wip_pwm_validate_map(wip_pwm_map) >= 0) {
    munmap((void *)wip_pwm_map, BLOCK_SIZE);
    wip_pwm_map = (uint32_t *)-1;
  }

  if (wip_pwm_validate_map(wip_clk_map) >= 0) {
    munmap((void *)wip_clk_map, BLOCK_SIZE);
    wip_clk_map = (uint32_t *)-1;
  }

  if (wip_clk_mem_orig != NULL) {
    free((void *)wip_clk_mem_orig);
    wip_clk_mem_orig = NULL;
  }

  if (wip_pwm_mem_orig != NULL) {
    free((void *)wip_pwm_mem_orig);
    wip_pwm_mem_orig = NULL;
  }

  syslog(LOG_INFO, "Finished cleaning up PWM features.");
  return 0;
}

// write register
void wip_reg_write(volatile uint32_t *ptr, int reg, uint32_t value)
{
  if (wip_pwm_validate_map(ptr) >= 0) {
    *(ptr + (reg >> 2)) = value;
  }
}

// read register 
uint32_t wip_reg_read(volatile uint32_t *ptr, int reg)
{
  if (wip_pwm_validate_map(ptr) >= 0) {
    return *(ptr + (reg >> 2));
  } 
  return 0;
}

int wip_cm_set_clk_src(int clk_src)
{
  // supported clk_srcs
  switch (clk_src) {
  case WIP_CM_CLK_SRC_OSC  : 
  case WIP_CM_CLK_SRC_PLLA :
  case WIP_CM_CLK_SRC_PLLC :
  case WIP_CM_CLK_SRC_PLLD :
  case WIP_CM_CLK_SRC_PLLH :
    break;
  default:
    return -1;
  }

  if (wip_pwm_validate_map(wip_clk_map) < 0) {
    return -2;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -3;
  }

  uint32_t timeout = 100 * 1000;
  uint32_t orig_pwm = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);
  uint32_t val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);

  // disable pwm
  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, 0);

  // disable clk
  val &= ~(WIP_CM_MSK_KILL | WIP_CM_MSK_ENAB);
  // change clk_src
  val = WIP_CM_BIT_PASSWD | (val & ~WIP_CM_MSK_CSRC) | clk_src;
  wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_CTL, val); 
  usleep(100);

  uint32_t reg_val;
  do { 
    usleep(1);
    reg_val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);
    reg_val &= WIP_CM_MSK_BUSY;
  } while ((timeout-- > 0) && (0 != reg_val));

  // enable clk
  val |= WIP_CM_MSK_ENAB;
  wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_CTL, val); 

  // enable pwm
  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, orig_pwm);

  if (timeout <= 0) {
    return -4;
  }

  return 0;
}

int wip_cm_get_clk_src(void)
{
  if (wip_pwm_validate_map(wip_clk_map) < 0) {
    return -1;
  }

  uint32_t val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);

  val &= WIP_CM_MSK_CSRC;

  return val;
}

char *wip_cm_get_clk_src_name(int clk_src)
{
  return (char *)g_wip_cm_clk_name[clk_src];
}

int wip_cm_set_freq(float freq)
{
  if (wip_pwm_validate_map(wip_clk_map) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -2;
  }

  uint32_t timeout = 100 * 1000;
  uint32_t orig_pwm = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);
  uint32_t val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);

  int clk_src = wip_cm_get_clk_src();
  int ret = wip_cm_check_freq_range(freq, clk_src);
  if (ret < 0) {
    return ret;
  }

  // disable pwm
  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, 0);

  // disable clk
  val &= ~(WIP_CM_MSK_KILL | WIP_CM_MSK_ENAB);
  val |= WIP_CM_BIT_PASSWD;
  wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_CTL, val); 
  usleep(100);

  uint32_t reg_val;
  do { 
    usleep(1);
    reg_val = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_CTL);
    reg_val &= WIP_CM_MSK_BUSY;
  } while ((timeout-- > 0) && (0 != reg_val));

  // change frequency
  float divisor = wip_cm_calc_divisor(freq, clk_src);
  int divi = wip_cm_calc_divi(divisor);
  int divf = wip_cm_calc_divf(divisor);
  uint32_t pwmdiv = WIP_CM_BIT_PASSWD | 
    ((WIP_CM_MSK_DIV & divi) << WIP_CM_SFT_DIV) | 
    (WIP_CM_MSK_DIVF & divf);
  wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_DIV, pwmdiv);

  // enable clk
  val |= WIP_CM_MSK_ENAB;
  wip_reg_write(wip_clk_map, WIP_CM_REG_PWM_CTL, val); 

  // enable pwm
  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, orig_pwm);

  if (timeout <= 0) {
    return -4;
  }

  return 0;

}

float wip_cm_get_freq(void)
{
  if (wip_pwm_validate_map(wip_clk_map) < 0) {
    return -1;
  }

  int clk_src = wip_cm_get_clk_src();
  uint32_t pwmdiv = wip_reg_read(wip_clk_map, WIP_CM_REG_PWM_DIV);
  
  int divi = (pwmdiv >> WIP_CM_SFT_DIV) & WIP_CM_MSK_DIV;
  int divf = pwmdiv & WIP_CM_MSK_DIVF;

  float divisor = (float)divi + ((float)divf / 1024);
  
  float freq = (float)g_wip_cm_clk_table[clk_src] / divisor;

  return freq;
}

// validate frequency range
static int wip_cm_check_freq_range(float freq, int clk_src)
{
  float maxf = WIP_CM_MAX_FREQ;

  if (freq > maxf) {
    return -1;
  }

  maxf = (float)g_wip_cm_clk_table[clk_src];

  // maximum frequeuncy check
  if (freq > maxf) {
    return -1;
  }

  float minf = (float)g_wip_cm_clk_table[clk_src] / WIP_CM_MSK_DIV;

  // minimum frequency check
  if (freq < minf) {
    return -1;
  }

  return 0;
}

// calculate divisor with frequency
static float wip_cm_calc_divisor(float freq, int clk_src)
{
  float div = 0.0F;

  if ( clk_src < WIP_CM_SIZE_CLK_SRC ) {
     div = ((float)g_wip_cm_clk_table[clk_src]) / freq;
  }

  return div;
}

// calculate difi value
static inline int wip_cm_calc_divi(float div)
{
  return (int)div;
}

// calculate divf value 
static int wip_cm_calc_divf(float div)
{
  int divi = wip_cm_calc_divi(div);
  int divf = (int)((div - divi) * 1024);

  return divf;
}

int wip_pwm_set_msmode(int ch, int msmode)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  if (WIP_PWM_PWM_MODE == msmode) {
    value &= ~(WIP_PWM_MSK_MSEN << (ch * WIP_PWM_CTL_SFT));
  } else {
    value |= (WIP_PWM_MSK_MSEN << (ch * WIP_PWM_CTL_SFT));
  }

  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, value);

  return 0;
}

int wip_pwm_get_msmode(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  if (0 != (WIP_PWM_MSK_MSEN & (value >> (ch * WIP_PWM_CTL_SFT)))) {
    return WIP_PWM_MS_MODE;
  } else {
    return WIP_PWM_PWM_MODE;
  }  
  return value;
}

int wip_pwm_set_polarity(int ch, int polarity)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  if (WIP_PWM_POLARITY_NORMAL == polarity) {
    value &= ~(WIP_PWM_MSK_POLA << (ch * WIP_PWM_CTL_SFT));
  } else {
    value |= WIP_PWM_MSK_POLA << (ch * WIP_PWM_CTL_SFT);
  }

  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, value);

  return 0;
}

int wip_pwm_get_polarity(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  if (0 != (WIP_PWM_MSK_POLA & (value >> (ch * WIP_PWM_CTL_SFT)))) {
    return WIP_PWM_POLARITY_REVERSE;
  } else {
    return WIP_PWM_POLARITY_NORMAL;
  }
}

int wip_pwm_enable(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  value |= (WIP_PWM_MSK_PWEN << (ch * WIP_PWM_CTL_SFT));

  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, value);

  return 0;
}

int wip_pwm_disable(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  value &= ~(WIP_PWM_MSK_PWEN << (ch * WIP_PWM_CTL_SFT));

  wip_reg_write(wip_pwm_map, WIP_PWM_REG_CTL, value);

  return 0;
}

int wip_pwm_is_enabled(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_CTL);

  if (0 != (value & (WIP_PWM_MSK_PWEN << (ch * WIP_PWM_CTL_SFT)))) {
    return 1;
  } else {
    return 0;
  }
}

// GPIO port
int wip_pwm_set_port(int ch, int port)
{
  int i;
  int cur_port;

  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  // set current HWPWM output port to in, if next port is different. 
  cur_port = wip_pwm_get_port(ch);
  if ((-1 != cur_port) && (port != cur_port)) {
    set_function(cur_port, IN, PUD_DOWN);
  }

  int rev = get_rpi_revision();

  for (i = 0 ; i < WIP_PWM_GPIO_PORTS; i++) {
    if (wip_pwm_map_table[i].gpio_port == port){
      if (rev >= wip_pwm_map_table[i].rpi_rev) {
	set_function(port, 
		     wip_pwm_map_table[i].alt_func,
		     wip_pwm_map_table[i].pullupdn);
	return 0;
      }
    }
  }

  return -1;
}

int wip_pwm_get_port(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  int i;

  for (i = 0 ; i < WIP_PWM_GPIO_PORTS; i++) {
    int port = wip_pwm_map_table[i].gpio_port;
    int func = get_function(port);
    if (func == wip_pwm_map_table[i].alt_func) {
      if (ch == wip_pwm_map_table[i].pwm_ch) {
	return port;
      }
    }
  }

  return -1;
}

int wip_pwm_set_period(int ch, int period)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }
  
  uint32_t value = period;
  wip_reg_write(wip_pwm_map, 
		WIP_PWM_REG_RNG1 + (WIP_PWM_REG_OFFSET * ch),
		value);  
  
  usleep(10);

  return 0;
}

int wip_pwm_get_period(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_RNG1 + (WIP_PWM_REG_OFFSET * ch));

  return value;
}

int wip_pwm_set_duty(int ch, int duty)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = duty;
  wip_reg_write(wip_pwm_map, 
		WIP_PWM_REG_DAT1 + (WIP_PWM_REG_OFFSET * ch),
		value);  

  return 0;
}

int wip_pwm_get_duty(int ch)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  uint32_t value = wip_reg_read(wip_pwm_map, WIP_PWM_REG_DAT1 + (WIP_PWM_REG_OFFSET * ch));

  return value;
}

int wip_pwm_set_period_ns(int ch, uint32_t period)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  // TODO 
  return -1;
}

int wip_pwm_set_duty_ns(int ch, uint32_t duty)
{
  if (wip_pwm_validate_ch(ch) < 0) {
    return -1;
  }

  if (wip_pwm_validate_map(wip_pwm_map) < 0) {
    return -1;
  }

  // TODO 
  return -1;
}

// validator
int wip_pwm_validate_ch(int ch)
{
  // check channel number
  if ( (ch < 0) || (ch >= WIP_PWM_NUM_OF_CH) ) {
    return -1;
  }

  return 0;
}

static inline int wip_pwm_validate_map(volatile uint32_t *ptr)
{
  if (((uint32_t *)-1 == ptr) || (NULL == ptr)) {
    return -1;
  }

  return 0;
}

#ifdef _UT_MODE
int main(int argc, char *argv[])
{
  return 0;
}
int get_rpi_revision(void)
{
  return 1;
}
int get_function(int gpio)
{
  return 0;
}
void set_function(int gpio, int function, int pud)
{
}
#endif // _UT_MODE
