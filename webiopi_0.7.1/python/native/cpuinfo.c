/*
Copyright (c) 2012-2016 Ben Croston

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
#include <stdlib.h>
#include <string.h>
#include "cpuinfo.h"

int get_rpi_revision(void)
{
   int ret ;
   rpi_info info;

   memset(&info, 0x00, sizeof(info));

   ret = get_rpi_info(&info);

   if (0 == ret) {
      return info.p1_revision;
   } else {
      return -1;
   }
}

int get_rpi_info(rpi_info *info)
{
   FILE *fp;
   char buffer[1024];
   char hardware[1024];
   char revision[1024];
   char *rev;
   int found = 0;
   int len;
   char *pbuf;

   memset(hardware, 0x00, sizeof(hardware));
   memset(revision, 0x00, sizeof(revision));

   if ((fp = fopen("/proc/cpuinfo", "r")) == NULL)
      return -1;
   while(!feof(fp)) {
      memset(buffer, 0x00, sizeof(buffer));
      pbuf = fgets(buffer, sizeof(buffer), fp);
      if (pbuf != NULL ) {
         sscanf(buffer, "Hardware	: %s", hardware);
      }
      if (strcmp(hardware, "BCM2708") == 0 ||
          strcmp(hardware, "BCM2709") == 0 ||
          strcmp(hardware, "BCM2711") == 0 ||
          strcmp(hardware, "BCM2835") == 0 ||
          strcmp(hardware, "BCM2836") == 0 ||
          strcmp(hardware, "BCM2837") == 0 ) {
         found = 1;
      }
      sscanf(buffer, "Revision	: %s", revision);
   }
   fclose(fp);

   if (!found)
      return -1;

   if ((len = strlen(revision)) == 0)
      return -1;

   if (len >= 6 && strtol((char[]){revision[len-6],0}, NULL, 16) & 8) {
      // new scheme
      //info->rev = revision[len-1]-'0';
      strcpy(info->revision, revision);
      //switch (revision[len-2]) {
      switch (strtol((char[]){revision[len-3],revision[len-2],0}, NULL, 16)) {
            case 0x00: info->type = "Model A"; info->p1_revision = 2; break;
            case 0x01: info->type = "Model B"; info->p1_revision = 2; break;
            case 0x02: info->type = "Model A+"; info->p1_revision = 3; break;
            case 0x03: info->type = "Model B+"; info->p1_revision = 3; break;
            case 0x04: info->type = "Pi 2 Model B"; info->p1_revision = 3; break;
            case 0x05: info->type = "Alpha"; info->p1_revision = 3; break;
            case 0x06: info->type = "CM 1"; info->p1_revision = 0; break;
            case 0x08: info->type = "Pi 3 Model B"; info->p1_revision = 3; break;
            case 0x09: info->type = "Zero"; info->p1_revision = 3; break;
            case 0x0a: info->type = "CM 3"; info->p1_revision = 3; break;
            case 0x0c: info->type = "Zero W"; info->p1_revision = 0; break;
            case 0x0d: info->type = "Pi 3 Model B+"; info->p1_revision = 3; break;
            case 0x0e: info->type = "Pi 3 Model A+"; info->p1_revision = 3; break;
            case 0x10: info->type = "CM 3+"; info->p1_revision = 3; break;
            case 0x11: info->type = "Pi 4 Model B"; info->p1_revision = 4; break;
            case 0x13: info->type = "Pi 400"; info->p1_revision = 4; break;
            case 0x14: info->type = "CM 4"; info->p1_revision = 4; break;
            default : info->type = "Unknown"; info->p1_revision = 3; break;
      }
      switch (revision[len-4]) {
            case '0': info->processor = "BCM2835"; break;
            case '1': info->processor = "BCM2836"; break;
            case '2': info->processor = "BCM2837"; break;
            case '3': info->processor = "BCM2711"; break;
            default : info->processor = "Unknown"; break;
      }
      switch (revision[len-5]) {
            case '0': info->manufacturer = "Sony"; break;
            case '1': info->manufacturer = "Egoman"; break;
            case '2': info->manufacturer = "Embest"; break;
            case '3': info->manufacturer = "Sony Japan"; break;
            case '4': info->manufacturer = "Embest"; break;
            case '5': info->manufacturer = "Stadium"; break;
            default : info->manufacturer = "Unknown"; break;
      }
      switch (strtol((char[]){revision[len-6],0}, NULL, 16) & 7) {
            case 0: info->ram = "256M"; break;
            case 1: info->ram = "512M"; break;
            case 2: info->ram = "1024M"; break;
            case 3: info->ram = "2048M"; break;
            case 4: info->ram = "4096M"; break;
            case 5: info->ram = "8192M"; break;
            default: info->ram = "Unknown"; break;
      }
   } else {
      // old scheme
      info->ram = "Unknown";
      info->manufacturer = "Unknown";
      info->processor = "Unknown";
      info->type = "Unknown";
      strcpy(info->revision, revision);

      // get last four characters (ignore preceeding 1000 for overvolt)
      if (len > 4)
         rev = (char *)&revision+len-4;
      else
         rev = revision;

      if ((strcmp(rev, "0002") == 0) ||
          (strcmp(rev, "0003") == 0)) {
         info->type = "Model B";
         info->p1_revision = 1;
         info->ram = "256M";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0004") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Sony";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0005") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Qisda";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0006") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Egoman";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0007") == 0) {
         info->type = "Model A";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Egoman";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0008") == 0) {
         info->type = "Model A";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Sony";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0009") == 0) {
         info->type = "Model A";
         info->p1_revision = 2;
         info->ram = "256M";
         info->manufacturer = "Qisda";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "000d") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "512M";
         info->manufacturer = "Egoman";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "000e") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "512M";
         info->manufacturer = "Sony";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "000f") == 0) {
         info->type = "Model B";
         info->p1_revision = 2;
         info->ram = "512M";
         info->manufacturer = "Qisda";
         info->processor = "BCM2835";
      } else if ((strcmp(rev, "0011") == 0) ||
                 (strcmp(rev, "0014") == 0)) {
         info->type = "Compute Module";
         info->p1_revision = 0;
         info->ram = "512M";
         info->processor = "BCM2835";
      } else if (strcmp(rev, "0012") == 0) {
         info->type = "Model A+";
         info->p1_revision = 3;
         info->ram = "256M";
         info->processor = "BCM2835";
      } else if ((strcmp(rev, "0010") == 0) ||
                 (strcmp(rev, "0013") == 0)) {
         info->type = "Model B+";
         info->p1_revision = 3;
         info->ram = "512M";
         info->processor = "BCM2835";
      } else {  // don't know - assume revision 3 p1 connector
         info->p1_revision = 3;
      }
   }
   return 0;
}

/*

32 bits
NEW                   23: will be 1 for the new scheme, 0 for the old scheme
MEMSIZE             20: 0=256M 1=512M 2=1G
MANUFACTURER  16: 0=SONY 1=EGOMAN
PROCESSOR         12: 0=2835 1=2836
TYPE                   04: 0=MODELA 1=MODELB 2=MODELA+ 3=MODELB+ 4=Pi2 MODEL B 5=ALPHA 6=CM
REV                     00: 0=REV0 1=REV1 2=REV2

pi2 = 1<<23 | 2<<20 | 1<<12 | 4<<4 = 0xa01040

--------------------

SRRR MMMM PPPP TTTT TTTT VVVV

S scheme (0=old, 1=new)
R RAM (0=256, 1=512, 2=1024)
M manufacturer (0='SONY',1='EGOMAN',2='EMBEST',3='UNKNOWN',4='EMBEST')
P processor (0=2835, 1=2836 2=2837)
T type (0='A', 1='B', 2='A+', 3='B+', 4='Pi 2 B', 5='Alpha', 6='Compute Module')
V revision (0-15)

*/

// thor 
float get_rpi_cpu_temp(void)
{
  FILE *fp = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
  int iTemp = 0;
  int ret = 0;
  if (NULL != fp) {
    ret = fscanf(fp, "%d", &iTemp);
    fclose(fp);
    fp = NULL;
    if (ret < 0) {
      return 0.0;
    }      
    return ((float)iTemp) / 1000.0 ;
  } else {
    return 0.0;
  }
}

