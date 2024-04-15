#!/bin/sh

BASEDIR=$(dirname $0)
echo \n
echo Input path to files directory or to a single file:
read pathName
echo Write the sample rates you want to convert to, separated with comma:
read sampleRates
python3 $BASEDIR/HeaderHacker.py -p $pathName -s $sampleRates