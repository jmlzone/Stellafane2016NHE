//
// adapted by James Lee jml@jmlzone.com
// This file is one of many created by or found by James Lee
// <jml@jmlzone.com> to help with the new horizon model for stellafane 2016.
//
// All the original files are CopyLeft 2016 James Lee permission is here
// by given to use these files for educational and non-commercial use.
// For commercial or other use please contact the author as indicated in
// the file or jml@jmlzone.com
// note: Original file and directions to use the C library found on line
// on message boards with any particular copyright notice.
// It is assumed those sources and directions are in the public domain.
//
// first install the c library per these instructions:
//http://www.airspayce.com/mikem/bcm2835/
// basically:
//  wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
//  tar xfz bcm2835-1.50.tar.gz 
//  cd bcm2835-1.50/
//  ./configure
//  make
//  sudo make check
//  sudo make install
//  sudo raspi-config
//  ls /proc/device-tree/soc/ranges 
//
// program must be run with sudo
//
//fordit:  gcc MLXi2c.c -o i2c -l bcm2835
#include <stdio.h>
#include <bcm2835.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#define AVG 10   //averaging samples
#define LOGTIME 10  //loging period
int main(int argc, char **argv)
{
    unsigned char buf[6];
    unsigned char i,reg;
    double atemp=0,acalc=0,otemp=0,ocalc=0, objtemp,ambtemp;
    FILE *flog;
    flog=fopen("/var/www/html/missions/mlxlog.csv", "w");
    bcm2835_init();
    bcm2835_i2c_begin();
    bcm2835_i2c_set_baudrate(25000);
    // set address
    bcm2835_i2c_setSlaveAddress(0x5a);
    printf("\nOk, your device is working!!\n");
    while(1) {
        time_t t = time(NULL);
	struct tm tm = *localtime(&t);
	acalc=0;
	ocalc=0;
	for(i=0;i<AVG;i++){
	  reg=7;
	  bcm2835_i2c_begin();
	  bcm2835_i2c_write (&reg, 1);
	  bcm2835_i2c_read_register_rs(&reg,&buf[0],3);
	  otemp = (double) (((buf[1]) << 8) + buf[0]);
	  otemp = (otemp * 0.02)-0.01;
	  otemp = otemp - 273.15;
	  ocalc+=otemp;
	  reg=6;
	  bcm2835_i2c_begin();
	  bcm2835_i2c_write (&reg, 1);
	  bcm2835_i2c_read_register_rs(&reg,&buf[0],3);
	  atemp = (double) (((buf[1]) << 8) + buf[0]);
	  atemp = (atemp * 0.02)-0.01;
	  atemp = atemp - 273.15;
	  acalc+=atemp;
	}
	objtemp=ocalc/AVG;
	ambtemp=acalc/AVG;
	//	printf("%02d-%02d %02d:%02d:%02d\n    Tambi=%04.2f C, Tobj=%04.2f C\n", tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec,ambtemp,objtemp);
	fprintf(flog,"%04d-%02d-%02d %02d:%02d:%02d,%04.2f,%04.02f\n",tm.tm_year+1900, tm.tm_mon +1, tm.tm_mday,tm.tm_hour, tm.tm_min, tm.tm_sec,atemp,objtemp);
	fflush(flog);
	//sleep(LOGTIME-(2*AVG));
    }
    printf("[done]\n");
}
