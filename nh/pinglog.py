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
import time
import RPi.GPIO as GPIO
import datetime
import os
import sys
import signal
from optparse import OptionParser
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)

def createParser ():
    usage = "Usage %s [options]" %__file__
    parser = OptionParser(usage)
    parser.add_option("--triggerpin", "-t",
                      dest = "trigpin",
                      default = 12,
                      action = "store",
                      type = "int",
                      help = "board pin to use for pinger trigger"
                      )
    parser.add_option("--echopin", "-e",
                      dest = "echopin",
                      default = 16,
                      action = "store",
                      type = "int",
                      help = "board pin to use for pinger echo"
                      )
    return(parser)
parser = createParser()
options,args=parser.parse_args()
GPIO.setmode(GPIO.BOARD)
trigpin = options.trigpin
echopin = options.echopin
GPIO.setup(trigpin,GPIO.OUT)
GPIO.setup(echopin,GPIO.IN)
GPIO.output(trigpin, False)
def ping():
    GPIO.output(trigpin, True)
    time.sleep(0.00001)
    GPIO.output(trigpin, False)
    while GPIO.input(echopin)==0:
        pulse_start = time.time()
        
    while GPIO.input(echopin)==1:
        pulse_end = time.time()      
            
    pulse_duration = pulse_end - pulse_start
            
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

htmlRoot = "/var/www/html"
logfile = os.path.join(htmlRoot, "missions", "distancelog.csv")
log = open(logfile,'w')
signal.signal(signal.SIGTERM, sigterm_handler)
try:
    while True: 
        time.sleep(0.10)
        distance = ping();
        t=datetime.datetime.now()
        #print t,",Distance:",distance,"cm"
        log.write("%s,%f\n" % (t,distance))
        log.flush()

finally:
    GPIO.cleanup()
    log.close()
    print "graceful exit"





