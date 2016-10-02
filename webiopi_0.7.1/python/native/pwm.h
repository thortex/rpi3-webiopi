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

#ifndef _WIP_PWM_H_
#define _WIP_PWM_H_

//
// This file provides WebIOPi Hardware PWM feature.
//

// ----------------------------------------------------------------------
// Common Definitions
//

// common
int wip_pwm_setup(int mem_fd);
int wip_pwm_cleanup(void);

// ----------------------------------------------------------------------
// CM

// Clock Sources 
#define WIP_CM_CLK_SRC_OSC  1 // 19.2 MHz from Xtal oscillator
#define WIP_CM_CLK_SRC_PLLA 4 // 650 MHz for Compact Camera Port 2 TX clock
#define WIP_CM_CLK_SRC_PLLC 5 // 200 MHz for Core VPU clock
#define WIP_CM_CLK_SRC_PLLD 6 // 500 MHz for DSI display PLL
#define WIP_CM_CLK_SRC_PLLH 7 // 216 MHz for HDMI AUX clock
#define WIP_CM_SIZE_CLK_SRC 8 // size of table
int wip_cm_set_clk_src(int clk_src);
int wip_cm_get_clk_src(void);
char *wip_cm_get_clk_src_name(int clk_src);

// frequency
int wip_cm_set_freq(float freq);
float wip_cm_get_freq(void);

// validator
#define WIP_PWM_NUM_OF_CH 2 // Maximum number of PWM channels
int wip_pwm_validate_ch(int ch);

// M/S mode
#define WIP_PWM_PWM_MODE 0
#define WIP_PWM_MS_MODE  1
int wip_pwm_set_msmode(int ch, int msmode);
int wip_pwm_get_msmode(int ch);

// polarity
#define WIP_PWM_POLARITY_NORMAL 0
#define WIP_PWM_POLARITY_REVERSE 1
int wip_pwm_set_polarity(int ch, int polartity);
int wip_pwm_get_polarity(int ch);

// pwm output control
int wip_pwm_enable(int ch);
int wip_pwm_disable(int ch);
int wip_pwm_is_enabled(int ch);
// GPIO port
int wip_pwm_set_port(int ch, int port);
int wip_pwm_get_port(int ch);
// period
int wip_pwm_set_period(int ch, int period);
int wip_pwm_get_period(int ch);

// duty
int wip_pwm_set_duty(int ch, int duty);
int wip_pwm_get_duty(int ch);

#endif /* _WIP_PWM_H_ */

