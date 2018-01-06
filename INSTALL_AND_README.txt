Much of the inspiration and the code came from the pyimagesearch.com website. Check this site out. It's fantastic, but don't do the pyimagesearch websites recommendation of compiling opencv on the raspberry - too much time and I could not get it to work. 

I've simplified the code so that it is more focussed for critter detection.

Here are the steps:

Step 0: 

Install hardware. 
1) Plug in the raspicam using the ribbon cable with the blue part of the ribbon facing away from the HDMI port.
2) Plug in a second USB camera - I got an inexpensive outdoor camera. This is the one I purchased for $41
ELP 1megapixel Day Night Vision Indoor&outdoor Cctv Usb Dome Housing Camera

Once you get the cameras working and the code below working, then you can make the outdoor housing for the camera. I just used a $15 plastic Stanley toolbox from Ace hardware - it worked GREAT as a water proof case for the raspberry pi, a powered usb hub, and power connectors (plenty of space and easy to cut with a Dremel). Here is the link...
http://www.acehardware.com/product/index.jsp?productId=11697110&cp=2568443.2568450.2628082.2629228


Step 1:

Plug your pi into a monitor and mouse/keyboard and log in.

Log your pi into your wifi network. I'll let you figure this out. Plenty of help on the web.

Determine the IP address of your raspberry pi - say with an ip scanner. Use this to putty or ftp or vnc over.

I use putty to log into my raspberry and nano to edit files. Emacs can also work, but be careful about tabs in emacs - can screw up python editing sometimes.

The following command will list your raspberry pi's ip address. This could change if you have multiple pi's or other devices logging into your wifi network.

sudo ifconfig 

Enable the camera and VNC server and set the keyboard (en_US UTC-9), and time zone under international options with the following command and menus:

sudo raspi-config

Step 2:

Update and install packages (this will take a loooong time - hours)

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-opencv
sudo apt-get install fswebcam # This allows you to attache a second USB camera for a second angle.
sudo apt-get install python-scipy
sudo apt-get install ipython # not necessary but useful
sudo pip install imtools 
sudo pip install dropbox # only if you will use dropbox (I don't recommend it and the code does not currently support this)
sudo apt-get install vnc # only if you want to connect remotely to the raspberry
sudo apt-get links2 # not necessary unless you do some of the fancy things below.

Step 3: 

Check out the camera - make sure it's acquiring video...

For the raspicamera...

raspivid -o out.h264

For a connected usb camera...

fswebcam image.jpg


Step 4: 

Now that this is done, ftp all of the python the files over from your pc - say with Filezilla. I put everything in /home/pi/Src/Python/Critter_Camera 

Steph 5: 

set up the cron job so that it starts upon reboot. How do we do this? (need to sudo)

sudo crontab -e

use nano and add these lines to the bottom... I like to reboot in case there is some unforseen crash. 

0 5 * * * sudo reboot
0 17 * * * sudo reboot
@reboot sudo python /home/pi/Src/Python/Critter_Camera/critter_camera.py --conf /home/pi/Src/Python/Critter_Camera/conf.json > /home/pi/cronlog.txt &

Step 6: 

edit json.conf with nano or your favorite editor and be sure the chosen pictures directly path is correct.

That should be it. Use top to see if python is running on reboot. It should take up at least 40% of the CPU. 
Walk in front of the camera and see if it snaps a photo.

I would recommend doing most of the fine tuning of the camera when it is directly connected to a monitor/keyboard so that you get instant feedback retgarding the focus (the raspicam is manual focus). Doing this remotely is much more of a hassle.



* OTHER: 

** Not recommended but I'll metion this stuff anyway: 

For streaming to vnc on your pc run this on raspi...
raspivid -o - -t 0 -hf -w 800 -h 400 -fps 24 |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8160}' :demux=h264
and then connect on your pc to the following address while using vlc..

192.168.30.0:8160

This can be useful if you are focusing the camera lens.
(FLAKEY THOUGH - got it to work once and then never again - don't waste your time.)

ALTERNATIVE: Use raspistill combined with links2 to view. How?
raspistill -t 60000 -tl 1000 -o a.jpg
The above will keep taking a pic every second for a long long time.
sudo apt-get install links2
links2 -g a.jpg
You must run the above in x windows so you get a window -duh
Then go to the menu - by clicking the bar above and choose refresh every time you wan a new image and then adjust focus. 

There seem to be some problems with the quality of the camera - but not sure why. 
