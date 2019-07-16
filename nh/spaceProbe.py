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
import picamera
import time
import socket
import os.path
import RPi.GPIO as GPIO
import subprocess
import sys
import smbus
import PCA9685
from threading import Timer

class board:
    def __init__ (self):
        ioPinDict = dict()
        ioPinDict['nh2016'] = {
            "pinger" : {"trigger" : 12, "echo" : 16},
            "odometer" : 22,
            "propulsion" : 18,
            "cameraMotor" : [32,40,38,36]
        }
        ioPinDict['cbp2019'] = {
            "pinger" : {"trigger" : 11, "echo" : 13},
            "odometer" : 29,
            "propulsion" : 31,
            "cameraMotor" : [32,40,38,36]
        }
        # see if we have an i2c pwm at 40
        self.i2cBus=smbus.SMBus(1)
        try:
            self.i2cBus.read_byte_data(0x40,0) # try a read
            self.havePWM = True
            self.pwm=PCA9685.PCA9685(i2c=self.i2cBus)
            self.board='cbp2019'
        except:
            print(" could not access i2c ", sys.exc_info()[0])
            self.havePWM = False
            self.board='nh2016'

        self.ioPinDict = ioPinDict[self.board]
        self.htmlRoot = "/var/www/html"


class Watchdog:
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
        
    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
        
    def stop(self):
        self.timer.cancel()
        
    def defaultHandler(self):
        print "default hanler called"
        raise self

class motor(object) :
    def __init__ (self,pins) :
        self.motorPins = pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.motorPins, GPIO.OUT)
        GPIO.output(self.motorPins,GPIO.LOW)    
        self.step=0;
        self.steps=[[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1],[1,0,0,1]]
        self.reverse = 0
        self.approachSteps = 1000
        self.normSteps = 500
        self.departSteps = 500
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

    def approach(self):
        global cam_pos
        self.go(self.approachSteps,-1)
        cam_pos = "approach"

    def normal(self):
        global cam_pos
        self.go(self.normSteps,1)
        cam_pos = "norm"

    def depart(self):
        global cam_pos
        m.go(self.departSteps,1)
        cam_pos = "dep"



#
# general program flow
# count off time or odometry and then take series of pictures.
# when using time, its elapsed time from launch.
# Time will be in seconds with ms resolution
# 
# there is a configuration array with
# Name of    time/odemetry         time of     time of      # of        
# object     before camera fwd     camera      camera       picures     camera
#            and picture start     normal      depart       to take     mode
# --------   -----------------     -------    --------     --------     --------
#
# subroutines

def launch():
    global cam_pos
    m.approach()
    cam_pos = "launch"

def getConfig():
    global mode
    configPath = configRoot + "/config.txt"
    if os.path.isfile(configPath):
        config = []
        file = open(configPath,"r")
        for line in file:
            fields = line.strip().split()
            if fields[0] == 'missionMode' :
                mode = fields[1]
            elif fields[0] == 'steps' :
                m.approachSteps = int(fields[1])
                m.normSteps = int(fields[2])
                m.departSteps = int(fields[3])
            else :
                config.append(fields)
        print "Read Config from file"
        print "mode = " + mode
    else:
        mode = "time"
        config = [
            ['Asteroid', 2.2,   3.5,  4.8,  1,      0],
            ['Jupiter' , 16.0,  18.5, 19.0, 1,      0],
            ['Pluto'   , 33.2,  34.5, 35.8, 1,      0]
        ]
        print "Using built in test config"
    sys.stdout.flush()
    return config

def odo(channel):
    global odoCtr
    odoCtr += 1
    print "(odo) %d" % odoCtr
    w.reset()

def odoTimeout():
    global odoCtr
    odoCtr = 10000
    print "Error: No odometry pulses in 10 seconds, Timing out mission"
    
def getTravelTime():
    global odoCtr
    if mode == 'time' :
        f = open("/proc/uptime", "r");
        t = float(f.read().split()[0])
        f.close()
    else :
        t = odoCtr
    return t

def travelTo(event_time, event_name):
    curr_time = getTravelTime()
    sleep_time = (launch_time + event_time) - curr_time
    print "Waiting %f to get to %s ... " % (sleep_time, event_name)
    sys.stdout.flush()
    if sleep_time > 0 and mode == 'time':
        time.sleep(sleep_time)
    else:
        while sleep_time > 0 :
            curr_time = getTravelTime()
            sleep_time = (launch_time + event_time) - curr_time
            time.sleep(0.01)

def capture (name, num_pic, camMode, nortime, deptime,):
    pname = htmlRoot + "/missions/" + hostname + "_" + sequence + "_" + name + "%d" + ".jpg"
    print "capturing %d images approaching %s" % (num_pic, name)
    camera.capture_sequence([pname %i for i in range(num_pic)], use_video_port=camMode)

    curr_time = getTravelTime()
    elapsed_time = curr_time - launch_time
    print "pos=%s et=%f, nt=%f, dt=%f" % (cam_pos,elapsed_time,nortime,deptime)
    travelTo(nortime, "normal %s" % event_name)
    m.normal()
    print "capturing %d images normal to %s" % (num_pic, name)
    camera.capture_sequence([pname %i for i in range(num_pic,(num_pic*2))], use_video_port=camMode)

    curr_time = getTravelTime()
    elapsed_time = curr_time - launch_time
    print "pos=%s et=%f, nt=%f, dt=%f" % (cam_pos,elapsed_time,nortime,deptime)
    travelTo(deptime, "depart %s" % event_name)
    m.depart()
    print "capturing %d images departing %s" % (num_pic, name)
    camera.capture_sequence([pname %i for i in range((2*num_pic),(num_pic*3))], use_video_port=camMode)
    
def sequenceNumber():
    sequencePath = configRoot + "/sequence.txt"
    if os.path.isfile(sequencePath):
        file = open(sequencePath)
        sequence = file.read()
        file.close()
        sequence = str(int(sequence) + 1)
    else:
        sequence = "1"
    file = open(sequencePath,"w")
    file.write(sequence)
    file.close()
    return sequence

# all default values below
def configCamera(camera):
    camera.sharpness = 0
    camera.contrast = 0
    camera.brightness = 50
    camera.saturation = 0
    camera.ISO = 0
    camera.video_stabilization = False
    camera.exposure_compensation = 0
    camera.exposure_mode = 'auto'
    camera.meter_mode = 'average'
    camera.awb_mode = 'auto'
    camera.image_effect = 'none'
    camera.color_effects = None
    camera.rotation = 0
    camera.hflip = False
    camera.vflip = False
    camera.crop = (0.0, 0.0, 1.0, 1.0)

def buildMissionWebPage():
    myMission = htmlRoot + "/missions/mission%s.html" % sequence
    html = open(myMission,"w");
    html.write("<html><body><h1>%s Mission %s results</h1>" % (hostname, sequence) )
    html.write("<a href=\"/\"><img src=/littleman_small.jpg><br>home</a><br>")
    html.write("<a href=\"/cgi-bin/launch.sh\">launch a new mission</a><br>")
    html.write("View <a href=\"/missions/mission.html\">most resent mission</a><br>")
    html.write("View all <a href=\"/missions/index.html\">mission index</a><br>")
    html.write("<a href=\"/cgi-bin/missionParams.pl\">Edit Mission Parameters</a><br>")
    html.write("<a href=\"/cgi-bin/motorTest.pl\">Motor Testing</a>")
    html.write("<hr><hr>\n");
    for event in config:
        name = event[0]
        num_pic = int(event[4])
        html.write("<h2>Mission past %s </h2>" % name)
        for i in range (0,(num_pic*3)) :
            html.write("image %d of %s<br>" % (i, name))
            pname = hostname + "_" + sequence + "_" + name + `i` + ".jpg"
            html.write("<img src=%s ><br>" % pname)
        html.write("<hr>\n");
    html.write("<hr>\n");
    html.write("Thermal profile<img src=thermal%s.gif><br>" % sequence)
    thermalData = "/missions/mlxlog%s.csv" % sequence
    html.write("<a href=%s>Detailed Thermal data in csv</a><br><br>" % thermalData)
    distanceData = "/missions/distancelog%s.csv" % sequence
    html.write("<a href=%s>Detailed distance data in csv</a><br><br>" % distanceData)
    html.write("<hr><hr>\n");
    html.write("<a href=\"/\">home</a><br>")
    html.write("<a href=\"/cgi-bin/launch.sh\">launch a new mission</a><br>")
    html.write("View <a href=\"/missions/mission.html\">most resent mission</a><br>")
    html.write("View all <a href=\"/missions/index.html\">mission index</a><br>")
    html.write("<a href=\"/cgi-bin/missionParams.pl\">Edit Mission Parameters</a><br>")
    html.write("<a href=\"/cgi-bin/motorTest.pl\">Motor Testing</a>")
    html.write("</body></html>")
    html.close()
    # update or create the mission index
    indexPath = htmlRoot + "/missions/index.html"
    if os.path.isfile(indexPath):
        index = open(indexPath, "a")
    else:
        index = open(indexPath,"w")
        index.write("<html><body><h1>Mission index</h1><br><ul>")
        index.write("<a href=\"/\"><img src=/littleman_small.jpg><br>home</a><br>")
        index.write("<a href=\"/cgi-bin/launch.sh\">launch a new mission</a><br>")
        index.write("View <a href=\"/missions/mission.html\">most resent mission</a><br>")
        index.write("View all <a href=\"/missions/index.html\">mission index</a><br>")
        index.write("<a href=\"/cgi-bin/missionParams.pl\">Edit Mission Parameters</a><br>")
        index.write("<a href=\"/cgi-bin/motorTest.pl\">Motor Testing</a><br>")
    index.write(("<li><a href=\"/missions/mission%s.html\"> Mission %s results</a></li>" % (sequence, sequence)))
    index.close()
    #create or update a link to the lastest mission
    missionPath = htmlRoot + "/missions/mission.html"
    if os.path.isfile(missionPath):
        os.remove(missionPath)
    os.symlink(myMission,missionPath)
    
# main program starts here
if __name__ == '__main__':
    hostname = socket.gethostname()

    odoCtr = 0
    # initialize camera
    try:
        camera = picamera.PiCamera()
    except:
        print("Oops camera did not initilize, In use or bad camera")
        exit(-1)
    cam_pos = "ready"
    mode = "time"
    b=board()
    htmlRoot = b.htmlRoot
    configRoot = htmlRoot + "/missions"
    # used in the pinger program:
    trigpin = b.ioPinDict['pinger']['trigger']
    echopin = b.ioPinDict['pinger']['echo']

    optionPin = b.ioPinDict['propulsion']
    # pin 20 is a ground
    odoPin = b.ioPinDict['odometer']
    motorPins = b.ioPinDict['cameraMotor']
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(odoPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(optionPin, GPIO.OUT)
    GPIO.add_event_detect(odoPin, GPIO.FALLING, callback=odo, bouncetime=30)
    GPIO.output(optionPin,GPIO.LOW)
    m=motor(motorPins)
    sequence = sequenceNumber()
    print "Preparing for launch of %s sequence %s" % (hostname, sequence)
    sys.stdout.flush()
    config = getConfig()
    print "Using steps:"
    print " Approach: %d" % m.approachSteps 
    print " Normal: %d" % m.normSteps
    print " Depart: %d" % m.departSteps

    configCamera(camera)
    camera.framerate = 30
    camera.start_preview()
    time.sleep(2)
    if mode != 'time' :
        w = Watchdog (10, odoTimeout)
        print "Set watchdog"

    pMlx=subprocess.Popen(['/home/pi/c/mlx2'])
    pingArgs = ['python', '/home/pi/nh/pinglog.py', '--triggerpin', "%s" % trigpin , '--echopin', "%s" % echopin]
    pPing=subprocess.Popen(pingArgs)
    time.sleep(0.25)
    launch()
    GPIO.output(optionPin,GPIO.HIGH)
    sys.stdout.flush()
    launch_time = getTravelTime()
    # we now use approach as the launch position camApproach()
    lastName = config[-1][0]
    for event in config:
        event_name = event[0]
        event_time = float(event[1])
        norm_time = float(event[2])
        depart_time = float(event[3])
        event_num_pic = int(event[4])
        event_camMode = bool(int(event[5]))
        travelTo(event_time,event_name)
        capture(event_name, event_num_pic, event_camMode, norm_time, depart_time)
        if event_name != lastName :
            m.approach()

    camera.close()
    pMlx.kill()
    pPing.kill()
    time.sleep(5.0)
    GPIO.output(optionPin,GPIO.LOW)
    time.sleep(0.25)
    GPIO.cleanup()
    print "Writing mission page"
    sys.stdout.flush()
    buildMissionWebPage()
    print "Plotting Data"
    #pargs = ['/home/pi/c/thermalPlot.sh', sequence]
    pargs = ['/home/pi/c/tpPlot.sh', sequence]
    p=subprocess.Popen( pargs )
    p.wait()
    print "Mission page complete"
    print "Use your browser back button, then view the mission index or most recent mission." 

### end ###

