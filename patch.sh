#!/bin/sh
# scp patch.sh cgi-bin/missionParams.pl pi@nh1:/home/pi/nh_stage
cd /home/pi/nh_stage
echo "set up cgi-bin"
mv missionParams.pl cgi-bin/
sudo cp cgi-bin/missionParams.pl /usr/lib/cgi-bin
sudo chmod a+rx /usr/lib/cgi-bin/*
