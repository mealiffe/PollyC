#!/bin/sh
# speak_to_file.sh for PollyC
# d. g. otto 2018/09/23

# commandline inputs
outfile="$1"
shift
text="$@"

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
$mydir/PollyC.$pytype --ofile "$mp3file" --text "$text" --cache "$mydir/$cachedir" --voiceid "$voice" --keyid "$keyid" --accesskey "$accesskey" --region "$region"

if test -f "$mp3file"
then
    # success - convert mp3 file to expected format
    avconv=$(which avconv || which ffmpeg)
    if test -x "$avconv"
    then
        # use avconv/ffmpeg if available
        $avconv -v error -i "$mp3file" -y -ar 44100 -ac 2 "$outfile"
    else
        # otherwise convert with  mpg123
        # determine expected format from outfile name
        echo "Output File: $outfile"
        case $outfile in
        *.wav | *.WAV )
            # convert mp3 to wav, remove mp3
            mpg123 -q -w "$outfile" "$mp3file"
            ;;
        * )
            # use mp3 as-is
            mv -f "$mp3file" "$outfile"
            ;;
        esac
    fi
    rm -f "$mp3file"
else
    # failure - fallback to standard HS3 method: flite
    # strip metatags from text
    text=$(echo "$text" | awk '{gsub("<[^>]*>", ""); print}')
    # to list voices available: flite -lv
    # Voices available: kal awb_time kal16 awb rms slt
    voice=awb
    flite -o "$outfile" -t "$text" -voice $voice
fi

# display output file info 
file $outfile
