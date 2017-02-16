#!/usr/bin/python
#
# copyleft 2016 James Lee jml@jmlzone.com
# This file is one of many created by or found by James Lee
# <jml@jmlzone.com> to help with the new horizon model for stellafane 2016.
#
# All the original files are CopyLeft 2016 James Lee permission is here
# by given to use these files for educational and non-commercial use.
# For commercial or other use please contact the author as indicated in
# the file or jml@jmlzone.com
#
#
# hardware setup infomation
# odemetry pulses on
#
# use onboard pi camera
#
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
trigpin = 12
echopin = 16
GPIO.setup(trigpin,GPIO.OUT)
GPIO.setup(echopin,GPIO.IN)
for i in range(10) :
    print "Distance Measurement In Progress"
    GPIO.output(trigpin, False)
    print "Waiting For Sensor To Settle"
    time.sleep(2)
    GPIO.output(trigpin, True)
    time.sleep(0.00001)
    GPIO.output(trigpin, False)
    #print "wait zero"
    while GPIO.input(echopin)==0:
        #time.sleep(0.00001)
        pulse_start = time.time()
        
    #print "wait one"
    while GPIO.input(echopin)==1:
        #time.sleep(0.00001)
        pulse_end = time.time()      
            
    pulse_duration = pulse_end - pulse_start
            
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print "Distance:",distance,"cm"

GPIO.cleanup()






