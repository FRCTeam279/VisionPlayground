#!/bin/sh
# launcher.sh
# navigate home, then here then execute the python script, then back home

cd /
cd home/pi/VisionPlayground
python3 autoDetect.py
cd /
