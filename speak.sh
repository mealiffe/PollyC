#!/bin/sh
# speak.sh for PollyC
# d. g. otto 2018/09/23

# commandline inputs
text="$1"

# this script name
myname=$(basename $0 .sh)
# where this script lives
mydir="$(dirname $0)"
# temporary file storage
tmpdir=/tmp

# read parameters
test -f $mydir/PollyC.keys && . $mydir/PollyC.keys

# create file "/tmp/tts.debug" to enable debug log
test -f $tmpdir/tts.debug && exec > $tmpdir/$myname.log 2>&1

# PollyC output file
mp3file="$tmpdir/$myname$$.mp3"

# if python3 is available, use PollyC.py3; else use Polly.py
which python3 >/dev/null && pytype=py3 || pytype=py

# generate mp3 file
$mydir/PollyC.$pytype --ofile "$mp3file" --text "$text" --cache "$mydir/$cachedir" --voiceid "$voice" --keyid "$keyid" --accesskey "$accesskey" --region "$region" --engine "$engine"

if test -f "$mp3file"
then
    # success - play, then remove file
    mpg123 -q $mp3file && rm -f $mp3file
else
    # failure - fallback to standard HS3 method - pick your poison, flite or pico
    # strip metatags from text
    text=$(echo "$text" | awk '{gsub("<[^>]*>", ""); print}')
    # to list flite voices available: flite -lv
    # Voices available: kal awb_time kal16 awb rms slt
    voice=awb
    flite -t "$1" -voice $voice
    wavfile="$tmpdir/$myname$$.wav"
    #pico2wave -w=$wavfile "$1" && aplay $wavfile && rm -f $wavfile
fi
