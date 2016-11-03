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
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <time.h>
#include <syslog.h>

#include "gpio.h"
#include "cpuinfo.h"
#include "pwm.h"

int show_revision_and_hardware(void)
{
  FILE *fp = NULL;
  char buffer[256];
  char *pbuf = NULL;

  fp = fopen("/proc/cpuinfo", "r");
  if (fp != NULL){
    while(!feof(fp)) {
      memset(buffer, 0x00, sizeof(buffer));
      pbuf = fgets(buffer, sizeof(buffer), fp);
      if (pbuf != NULL) {
	if (strstr(pbuf, "Hardware")){
	  printf("%s", pbuf);
	}
	if (strstr(pbuf, "Revision")){
	  printf("%s", pbuf);
	}
      }
    }
    fclose(fp);
    fp = NULL;
  }
  
  return 0;
}

int show_gpio_base(void)
{
  FILE *fp = NULL;
  unsigned char buf[4];

  memset(buf, 0x00, sizeof(buf));

  fp = fopen("/proc/device-tree/soc/ranges", "rb");
  if (fp != NULL){
    fseek(fp, 4, SEEK_SET);
    if (fread(buf, 1, sizeof(buf), fp) == sizeof(buf)) {
      printf("Base Address    : %02x%02x%02x%02x\n", buf[0], buf[1], buf[2], buf[3]);
    }
    
    fclose(fp);
  }

  return 0;
}

int show_model(void)
{
  FILE *fp = NULL;
  char buffer[256];
  char *pbuf = NULL;

  fp = fopen("/proc/device-tree/model", "r");
  if (fp != NULL){
    while(!feof(fp)) {
      memset(buffer, 0x00, sizeof(buffer));
      pbuf = fgets(buffer, sizeof(buffer), fp);
      if (pbuf != NULL) {
	printf("Model           : %s\n", pbuf);
      }
    }
    fclose(fp);
    fp = NULL;
  }
  
  return 0;
}


int main(int argc, char *argv[])
{
  int found = 0;
  rpi_info info;

  memset(&info, 0x00, sizeof(info));
  found = get_rpi_info(&info);
  show_model();
  show_revision_and_hardware();
  show_gpio_base();  
  printf("Build Date      : %s\n", __DATE__);
  printf("Build Time      : %s\n", __TIME__);  
  printf("CPU Temperature : %.2f\n", get_rpi_cpu_temp());
  printf("Number of Cores : %d\n", number_of_cores());
  printf("Revision        : %d\n", get_rpi_revision());
  printf("Found           : %s\n", (found == 0)? "Yes": "No");
  printf("RAM             : %s\n", info.ram);
  printf("Manufacturer    : %s\n", info.manufacturer);
  printf("Processor       : %s\n", info.processor);
  printf("Type            : %s\n", info.type);
  printf("Revision        : %s\n", info.revision);
  printf("P1 Revision     : %d\n", info.p1_revision);


  return 0;
}


