#Header Hacker

Hack the header of a wave file, to change the interpreted sample rate.  
The script does not do sample rate conversion or time stretch, but change sample rate in the header of the file.
This means a file of 88.2kHz, changed with the script to be played as 44.1kHz, would play at half the speed.

Usage

* make sure Python3 is installed. 
* open commandline of your choice and cd to folder with main.py
* use python3 and run HeaderHacker.py with: -p path-to-files -s sample,rates,with,comma
* example of use: python3 HeaderHacker.py /Users/Samples/FilesToBeConverted -s 44100,1500,22050
* Wait for processing and done message and new files will have been converted at location.
