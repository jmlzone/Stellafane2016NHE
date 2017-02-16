#!/bin/sh
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
missionNum=$1
gnuplot <<EOF
set term gif small
set output "thermal.gif"
set datafile separator ","
set xdata time
set x2data time
set timefmt "%Y-%m-%d %H:%M:%S"
set format x "%S"
set style data lines
set noautoscale y
set yrange [10:40]
set ytics nomirror 10,5,40
set xlabel "Seconds"
set ylabel "temp C"
plot "/var/www/html/missions/mlxlog.csv" using 1:2 title "ambient", "/var/www/html/missions/mlxlog.csv" using 1:3 title "object"

EOF

cp thermal.gif /var/www/html/missions/thermal${missionNum}.gif
mv /var/www/html/missions/mlxlog.csv /var/www/html/missions/mlxlog${missionNum}.csv



