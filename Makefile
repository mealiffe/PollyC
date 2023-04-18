# Makefile for PollyC installation
# d. g. otto 2018/09/23

## usage:

# sudo make install-pollyc keyid=your_keyid accesskey=your_accesskey region=your_region voice=Voice

# region defaults to 'us-west-1'
# keyid, accesskey, region & voice can be hard-coded in the '01settings' file

##########################

include 01settings

installpoint := $(shell dirname $(shell dirname $(firstword $(foreach dir, $(installpoints), $(wildcard $(dir)/HomeSeer/HSConsole.exe)) ${installpoint}/././)))

SHELL=/bin/bash
ZIPFILE=PollyC-installer.zip
hs3root=${installpoint}/HomeSeer
keyfile=${hs3root}/PollyC.keys
cachedir=PollyCache

.PHONY: usage install-pollyc install-keys install-scripts install-pip install-boto3 install-mpg123 install-avconv install-flite install-pico
.PHONY: zip unzip clean

# default is to show usage
usage:
	@echo "usage: sudo make install-pollyc keyid=your_keyid accesskey=your_secret [ region=your-region-x ] [ voice=Voice ] [ engine=Engine ]"

# install PollyC source files and the modified speak.sh and speak_to_file.sh
install-pollyc: install-boto3 install-mpg123 install-avconv install-flite install-pico install-scripts
# don't overwrite existing keyfile unless new credentials provided
	test -f ${keyfile} -a "${keyid}" = your_keyid || make install-keys

install-keys: superuser
	@echo "Creating key file..."
	${file >${keyfile},# PollyC configurable parameters read by speak.sh, speak_to_file.sh}
	${file >>${keyfile},keyid="${keyid}"}
	${file >>${keyfile},accesskey="${accesskey}"}
	${file >>${keyfile},region="${region}"}
	${file >>${keyfile},voice="${voice}"}
	${file >>${keyfile},engine=${engine}"}
	${file >>${keyfile},cachedir="${cachedir}"}
	chmod 600 ${keyfile}

install-scripts: superuser
	install -p PollyC.py PollyC.py3 speak.sh speak_to_file.sh ${hs3root}

# install python pip
install-pip: superuser
	apt-get -qy install python-pip python3-pip

# install AWS boto3 package
install-boto3: install-pip
	pip install boto3
	pip3 install boto3

# install mpg123 MP3 player
install-mpg123: superuser
	apt-get -qy install mpg123

# install avconv/ffmpeg media converter, if available
install-avconv: superuser
	-apt-get -qy install libav-tools || apt-get -qy install ffmpeg

## ensure default audio tools are installed, in case of fall-back

# install flite (festival-lite) speech synthesis package
install-flite: superuser
	apt-get -qy install flite

# install pico2wave TTS engine
install-pico: superuser
	apt-get -qy install libttspico-utils

# check for super-user access
superuser:
	@test ${shell id -u} -eq 0 || (echo "Super-user access required - please use 'sudo'." && exit 1)

## developer tools

# create project archive
zip: $(ZIPFILE)
$(ZIPFILE): Makefile 01settings PollyC.py PollyC.py3 speak.sh speak_to_file.sh
	-zip $(ZIPFILE) $?

# update changed project files
unzip:
	unzip -uo $(ZIPFILE)

# remove project archive
clean:
	rm -f $(ZIPFILE)

