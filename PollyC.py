#!/usr/bin/python
# vim: ft=python
# PollyC.py version 0.10.0
# This module is used to call the Amazon Polly system to convert an incomming string
# to a audio file.
# Calling sequence
#   ./scripts/PollyC.py -o "output_file" -t "the text to speak" -c "./pollycache/" -k "key_ID" -a Key"
#
# arguments
#
#   -o or --ofile           Output file name
#   -t or --text            Text to speak
#   -v or --voiceid         The Polly voice to use (default = Joanna)
#                               see https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
#   -f or --format          Output format (default - mp3)
#   -c or --cache           cache directory, full, relative path or none
#                               If no cache is specified then cacheing is disabled
#   -k or --keyid           Amazon AWS Access Key ID, mandatory
#   -a or --accesskey       Amazon AWS Access Key, mandatory
#   -r or --region          Amazon Region (defaults to us-west-1)
#                               see https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
#
# PollyC will auto switch to ssml if it detects the string "<speak>" in the text to be converted.
#
# For instructions on how to encode ssml speech see https://docs.aws.amazon.com/polly/latest/dg/supported-ssml.html
#
#
# Select voice on call
# There is no provision in Amazon Polly to set the voice in the text string. However
# PollyC has the ability to do this: If you specify at the beginning of the text
# string, either plain text or ssml text, <voice-id="voice name"> then that voice will be
# used and the tag deleted from the string. This tag MUST be at the beginning of the string.
# Example:  '<voice-id="Matthew">This is a test'
#           '<voice-id="Matthew"><speak>This is a test</speak>'
#
# Don't cache this call.
# Currently PollyC will cache only if a caching directory is specified. This addition
# will allow each call to be cached or not.
# Usage: '<no-cache/>This is a test'
#        '<no-cache/><speak>This is a test</speak>'
#
# This program is free to use and distribute as long as the credits are not removed.
# Credit to DeLicious for figuring out the way to call Polly.
__author__ = 'John Warren'
#
# Import modules
#
import sys
import optparse
import shutil
import os
import hashlib
import boto3
import re
import unicodedata
#
# Define the main module
#
def main(argv):
#

    desc="""%prog takes a text string and passes it through Amazon Polly then returns
the resulting speech file.\nIn addition %prog will optional cache the resulting file in a
a cache directory. If no cache directory is specified the resulting speech will not be
cached. If a caching directory is specified and it does not exist it will be created.
%prog will automatically handle either plain text or ssml input strings."""

#
# Fetch arguments
#
    parser = optparse.OptionParser(description=desc)
# The mandatory parameters
    parser.add_option("-o", "--ofile", type="string", help="Output Speech File, mandatory", dest="ofile", default="")
    parser.add_option("-t", "--text", type="string", help="Input text string, mandatory", dest="text", default="")
    parser.add_option("-k", "--keyid", type="string", help="Amazon Access Key ID, mandatory", dest="key_id", default="")
    parser.add_option("-a", "--accesskey", type="string", help="Amazon Access Key, mandatory", dest="access_key", default="")
# The optional parameters
    parser.add_option("-c", "--cache", type="string", help="Cache Directory, if none then speech will not be cached", dest="cache", default="")
    parser.add_option("-v", "--voiceid", type="string", help="Voice to use", dest="voice", default="Joanna")
    parser.add_option("-f", "--format", type="string", help="Output Audio Format", dest="format", default="mp3")
    parser.add_option("-r", "--region", type="string", help="Region, defaults to us-west-1", dest="region", default="us-west-1")
    parser.add_option("-e", "--engine", type="string", help="Engine, defaults to standard", dest="engine", default="standard")

    (opts, args) = parser.parse_args()
    # Making sure all mandatory options appeared.
    mandatories = ['ofile', 'text', 'key_id', 'access_key']
    for m in mandatories:
        if not opts.__dict__[m]:
            print "mandatory option is missing\n"
            parser.print_help()
            exit(-1)
# Setup the parameters
    outputfile = opts.ofile
    text = opts.text
    a_aws_access_key_id = opts.key_id
    a_aws_secret_access_key = opts.access_key
    a_region = opts.region
    a_voice = opts.voice
    a_format = opts.format
    a_cachedir = opts.cache
    a_engine = opts.engine

# Make sure there is no trailing '/' in the cache directory name.
# This also prevents the director from being place in the root.
    a_cachedir = a_cachedir.rstrip('/')

    # texttype is 'text' unless <speak> tag encountered below
    a_texttype = 'text'

    # process metatags
    while True:
        m = re.search('^<.*?>', text)
        if m:
            mtag = m.group(0).lower()

            # <speak> tag goes goes to Polly
            if mtag == '<speak>':
                a_texttype = 'ssml'
                break
            # otherwise strip metatag from front of text
            text = text[len(mtag):]

            # process metatag '<voice-id="voice_name">'
            m = re.search('<voice-id="(.*?)">', mtag)
            if m:
                a_voice = m.group(1)

            # process metatag '<voice-engine="engine_name">'
            m = re.search('<voice-engine="(.*?)">', mtag)
            if m:
                a_engine = m.group(1)

            # process metatag '<no-cache>'
            elif mtag == '<no-cache>':
                a_cachedir = ''
            else:
                print 'Warning: metatag', mtag, 'ignored'

        else:
            break

#
# Create the hash object use to create the filename for the text string
#
    a_voice = a_voice.capitalize()
    hashobj = hashlib.sha512()
    hashtext = a_voice + '~' + text
    hashtext = ''.join(c for c in unicodedata.normalize('NFD', hashtext.decode('utf-8')) if unicodedata.category(c) != 'Mn')
    hashobj.update(hashtext.encode('utf-8'))
    hashfile = hashobj.hexdigest()
    filepath = a_cachedir+'/'+hashfile+'.'+a_format
#
# Create cache directory if it doesn't exist
#
    if a_cachedir and not os.path.exists(a_cachedir):
        os.makedirs(a_cachedir)

# Print out variables for testing
    print 'Region:', a_region
    print 'Key ID:', a_aws_access_key_id
    print 'Key:', a_aws_secret_access_key
    print 'Text:', text, '\nVoice:', a_voice, '\nFormat:', a_format
    print 'Text Type:', a_texttype
    print 'Polly Output:', outputfile
    if a_cachedir:
        print 'Cache File:', filepath
        print 'Cache Hit:', os.path.isfile(filepath)
#    exit(0) #exit for now
#
# Check to see if the cache exists and the file exists in the cache.
# If so copy cache file to output file, otherwise call Amazon Polly to generate it
#
    if a_cachedir and os.path.isfile(filepath):
        # Now copy the cached file to the destination.
        shutil.copyfile(filepath, outputfile)
    else:
#
# The interface to connect to Polly was written by DeLicious
# Create the Polly Object and call Polly to do the conversion
#
        polly = boto3.client('polly', region_name=a_region, aws_access_key_id=a_aws_access_key_id, aws_secret_access_key=a_aws_secret_access_key)
        response = polly.synthesize_speech(OutputFormat=a_format, Text=text, VoiceId=a_voice, TextType=a_texttype, Engine=a_engine)
#
# Now if there is a cache then put the file in the cache for later use
#
        if a_cachedir:
            # Copy to cache then to output file
            with open(filepath, 'wb') as f:
                for chunk in iter(lambda: response['AudioStream'].read(4096), b''):
                    f.write(chunk)
            shutil.copyfile(filepath, outputfile)
        else:
            # Don't cache, just copy to output
            with open(outputfile, 'wb') as f:
                for chunk in iter(lambda: response['AudioStream'].read(4096), b''):
                    f.write(chunk)

# End of Amazon Polly interface

if __name__ == "__main__":
        main(sys.argv[1:])

