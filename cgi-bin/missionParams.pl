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
$|=1;
require "cgi_handlers.pl" ;
my @config=();
my @row=();
my $r=0;
my $c=0;
my $elem;
my $mode;
my $missionMode;
my $configFile = "/var/www/html/missions/config.txt";
use Sys::Hostname;
my $hostname = hostname;

($mode = $ARGV[0]) =~ s/:.*$//;
&get_request;
if($mode =~ /^post$/){
  &post;
} else {
    &display_full_form;
}
sub display_full_form{
    &html_header("Mission Paramaters");
print <<EOF;
<H1>
Mission Paramaters for $hostname
</H1>
<a href="/"><img src=/littleman_small.jpg><br>home</a><br>
EOF

&display_sub_form;
}

sub display_sub_form{
if( -r "$configFile" ) {
    open(CONFIG, "$configFile") || die "error opening $configFile for read";
    while (<CONFIG>) {
	@row = split;
	if($row[0] eq "missionMode") {
	    $missionMode = $row[1];
	} elsif($row[0] eq "steps") {
	    @steps = ($row[1],$row[2],$row[3]);
	} else {
	    push(@config, [@row]);
	}
    }
    close(CONFIG);
} else {
    $missionMode = "time";
    @steps = (1000,500,500);
    @config = ( ["Asteroid",0.2,1.5,2.8,1,0], ["Jupiter",7.0,8.5,10.0,1,0],["Pluto",13.2,14.5,15.5,1,1] );
}
    $rows = @config;
    $cols = 6;

print <<EOF;
<form action="/cgi-bin/missionParams.pl?post" method="post">
<table>
<tr>
<th scope="col">Motor</th>
<th scope="col">To Approach</th>
<th scope="col">To Normal</th>
<th scope="col">To Depart</th>
</tr>
<td>steps</td>
EOF
for ($c=0; $c < 3; $c++) {
    $elem = $steps[$c];
    print "<td><input type=text name=\"steps${c}\" value=\"${elem}\" size=10 /></td>\n";
}
print "</tr>\n";

print <<EOF;
</table>
<table>
<tr>
<th scope="col">Target</th>
<th scope="col">Approach</th>
<th scope="col">Normal</th>
<th scope="col">Depart</th>
<th scope="col">Num.</th>
<th scope="col">Picture</th>
</tr>
<tr>
<th scope="col">Name</th>
<th scope="col">Time</th>
<th scope="col">Time</th>
<th scope="col">Time</th>
<th scope="col">Picture</th>
<th scope="col">Mode</th>
</tr>
EOF
for ( $r=0; $r < @config; $r++) {
    print "<tr>\n" ;
    @row=$config[r];
    for ($c=0; $c < ($cols -1); $c++) {
	$elem = $config[$r][$c];
	print "<td><input type=text name=\"r${r}c${c}\" value=\"${elem}\" size=10 /></td>\n";
    }
    $c = ($cols -1);
    if($config[$r][$c]) {
	$hsChecked = "checked";
	$hdChecked = "";
    } else {
	$hsChecked = "";
	$hdChecked = "checked";
    }
    print "<td><input type=\"radio\" name=\"r${r}c${c}\" value=\"hs\" $hsChecked> High Speed";
    print "<input type=\"radio\" name=\"r${r}c${c}\" value=\"hd\" $hdChecked> High Def";
    print "</tr>\n";
}
if ($missionMode eq  "time") {
    $timechecked = "checked";
    $odochecked ="";
} else {
    $timechecked = "";
    $odochecked ="checked";
}

print <<EOF;
</table>
    <input type="radio" name="missionMode" value="time" $timechecked> Elapsed time from launch
    <input type="radio" name="missionMode" value="odo" $odochecked> Odometry <br>
<input type="hidden" name="rows" value="$rows">
<input type="hidden" name="cols" value="$cols">
    <input type="submit"value="Save" />
    <INPUT TYPE="reset" VALUE="Reset">      
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
    $rows = $rqpairs{"rows"};
    $cols = $rqpairs{"cols"};
    @steps = ($rqpairs{"steps0"},$rqpairs{"steps1"},$rqpairs{"steps2"});
    $missionMode = $rqpairs{"missionMode"};
    &html_header("Mission Paramaters Processed");
    print "<a href=\"/\"><img src=/littleman_small.jpg><br>home</a><br>\n";
    print "<H1>Mission Paramaters Processed for $hostname</H1>";
    print "rows = $rows, cols = $cols<br>\n";
    open(CONFIG, ">$configFile") || die "error opening $configFile for write";
    print "missionMode $missionMode<br>\n";
    print "steps: @steps<br>\n";
    print CONFIG "missionMode $missionMode\n";
    print CONFIG "steps @steps\n";
    for ($r=0; $r < $rows; $r++) {
	for ($c=0; $c < $cols; $c++) {
	    $idx = "r${r}c${c}";
	    $val  = $rqpairs{"$idx"};
	    print "$val ";
	    if($val eq "hd") {$val = 0;}
	    if($val eq "hs") {$val = 1;}
	    print CONFIG "$val ";
	}
	print "<br>\n";
	print CONFIG "\n";
    }
    print "<hr>\n";
    print "<br>\n";
    close(CONFIG);
    &display_sub_form;
}
