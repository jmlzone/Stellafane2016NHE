#!/usr/bin/python
import sys
import time
import RPi.GPIO as GPIO
import spaceProbe as board
#Note: import motor and board config from spaceProbe
# detect board type
b=board.board()
m=board.motor(b.ioPinDict['cameraMotor'])

# -1 = approach
# +1 = depart
steps = int(sys.argv[1])
if(sys.argv[2] == 'depart') :
    dir = 1
else:
    dir = -1


m.reverse = 0
startTime = time.time()
m.go(steps,dir)
m.off()
endTime=time.time()
t = endTime-startTime
sps = steps/t
print "Stepped %d steps toward %s (%d) in %f seconds or %f steps/second" % (steps,sys.argv[2],dir,t,sps)
GPIO.cleanup()
