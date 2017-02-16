#!/usr/bin/perl
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
use Sys::Hostname;
my $hostname = hostname;
$|=1;
require "cgi_handlers.pl" ;
($mode = $ARGV[0]) =~ s/:.*$//;
&get_request;
if($mode =~ /^post$/){
  &post;
} else {
    &display_full_form;
}
sub display_full_form{
    &html_header("Motor Testing");
    $steps = 100;
    $direction = "depart";
    &display_sub_form;
}
sub display_sub_form{
    if($direction eq "depart") {
	$departChecked = "checked";
	$approachChecked = "";
    }else{
	$departChecked = "";
	$approachChecked = "checked";
    }
print <<EOF;
<H1>
Motor Testing on $hostname
</H1>
<a href="/"><img src=/littleman_small.jpg><br>home</a><br>
<form action="/cgi-bin/motorTest.pl?post" method="post">
Motor steps (between 1 and 2000):
    <input type="number" name="steps" min="1" max="2000" value=$steps> 
    <input type="radio" name="direction" value="depart" $departChecked> depart
    <input type="radio" name="direction" value="approach" $approachChecked > approach <br>
    <input type="submit"value="Test" />
</form>

<body>
<hr>
    <a href="/">home</a><br>
    Click to <a href="/cgi-bin/launch.sh">launch</a> a new mission<br>
    View <a href="/missions/mission.html">most recent mission</a><br>
    View all <a href="/missions/index.html">mission index</a><br>
    <a href="/cgi-bin/missionParams.pl">Edit Mission Parameters</a><br>
    <a href="/cgi-bin/motorTest.pl">Motor Testing</a>

</body>
</html>
EOF
}

sub post{
    $steps = $rqpairs{"steps"};
    $direction = $rqpairs{"direction"};
    &html_header("Motor Test Results");
    print "<H1>Motor Test Results from $hostname</H1>";
    $output = system("sudo python /home/pi/nh/motorTest.py $steps $direction");
    print $output;
    print "\n<br>\n";
    &display_sub_form;
}
