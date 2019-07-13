#!/bin/sh
# scp patch2.sh cgi-bin/reboot.sh cgi-bin/shutdown.sh html/index.html nh/spaceProbe.py  pi@nh3:/home/pi/nh_stage
cd /home/pi/nh_stage
echo "set up cgi-bin"
mv reboot.sh shutdown.sh cgi-bin/
sudo cp cgi-bin/shutdown.sh cgi-bin/reboot.sh /usr/lib/cgi-bin
sudo chmod a+rx /usr/lib/cgi-bin/*
echo "----------------------------------------------------------------------"
echo "set up html"
mv index.html html
sudo cp html/index.html /var/www/html
sudo chmod a+r /var/www/html/*
echo "----------------------------------------------------------------------"
echo "set up main python in nh directory"
mv spaceProbe.py nh/
cp nh/spaceProbe.py ~/nh
chmod a+x nh/*

