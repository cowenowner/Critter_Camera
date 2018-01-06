
#!/bin/bash
#
# For streaming to vlc on your pc run this on raspi...
# 1: install vlc on the pi:  sudo apt-get install vlc
#
# Run this script and then connect on your pc to the following address/port while using vlc..
# 192.168.30.0:8160
# This can be useful if you are focusing the camera lens.
# Cowen - google streaming video on raspbian for more help...
echo "Running streaming video...."
/opt/vc/bin/raspivid -o - -t 0 -hf -w 800 -h 400 -fps 24 |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8554}' :demux=h264
echo "DONE"
