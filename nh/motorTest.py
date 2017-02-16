#!/usr/bin/python
import sys
import time
import RPi.GPIO as GPIO


class motor(object) :
    def __init__ (self) :
        self.motorPins = [32,40,38,36]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.motorPins, GPIO.OUT)
        GPIO.output(self.motorPins,GPIO.LOW)    
        self.step=0;
        #self.steps=[[1,1,0,1], [1,0,0,1], [1,0,1,1], [0,0,1,1], [0,1,1,1], [0,1,1,0], [1,1,1,0], [1,1,0,0] ]
        self.steps=[[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]
        self.reverse = 0
    def go(self,num,dir) :
        GPIO.output(self.motorPins,self.steps[self.step])
        if dir <1 :
            dir = -1
        else :
            dir = 1
        if(self.reverse==0) :
            dir = - dir
        for i in range(num) :
            self.step = (self.step + dir) % 8
            GPIO.output(self.motorPins,self.steps[self.step])
            time.sleep(0.002)
        GPIO.output(self.motorPins,GPIO.LOW)    
    def off(self) :
        GPIO.output(self.motorPins,[0,0,0,0])

#print "Number of arguments %d " % len(sys.argv)
#print "argument list", str(sys.argv)
#print "arg 1 = " + sys.argv[1]

# -1 = approach
# +1 = depart
steps = int(sys.argv[1])
if(sys.argv[2] == 'depart') :
    dir = 1
else:
    dir = -1

m=motor()
m.reverse = 0
startTime = time.time()
m.go(steps,dir)
m.off()
endTime=time.time()
t = endTime-startTime
sps = steps/t
print "Stepped %d steps toward %s (%d) in %f seconds or %f steps/second" % (steps,sys.argv[2],dir,t,sps)
GPIO.cleanup()
