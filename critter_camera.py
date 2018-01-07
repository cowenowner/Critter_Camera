# -*- coding: utf-8 -*-
"""
Back yard wild animal (or person) detection with the Raspberry Pi, Python, and OpenCV
This code is borrowed heavily from examples on pyimagesearch.com. Check out this site 
for some great tutorials.

The code requires the conf.json file (this directory). Specify the file on the call 
to critter_camera.py using the --conf or -c switches.

# HOW TO RUN:

python critter_camera.py -c json.conf

Or, if permissions are an issue (for some strange reason)...

sudo python critter_camera.py -c json.conf

The GitHub site is

www.github.com/cowenowner/Critter_Camera


The code from pyimagesearch also allows synchonization with Dropbox. I removed this 
as windy days can cause your dropbox folder to fill up fast. Instead, I just ftp the 
images over WiFi.

@author: Stephen Cowen and inspired from pyimagesearch.com
scowen [at ] email.arizona.edu
Created on Mon Jul 25 22:19:11 2016

"""

# import the necessary packages
from subprocess import call
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import sys
import csv
import os

# construct the argument parser and parse the arguments from the conf file (json)
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
args = vars(ap.parse_args())

# Initialize variables:
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
res = conf["resolution"]
conv_size = res[0]/20
client = None
np.set_printoptions(precision=4)

pictures_dir = conf["pictures_dir"]
usbfname = pictures_dir + "usbcam_tmp.jpg"

thresh_buffer_size = 10*60*4
thresh_buffer = np.zeros(shape = (thresh_buffer_size,1))
thresh_buffer_count = 0
toggle_camera = 1

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
# Open a text file for writing threshold values.
timestamp = datetime.datetime.now()
ts = timestamp.strftime("%h%d%H")

fname = conf["pictures_dir"] + 'threshold_file%s.csv' % (ts)
print(fname)

fp = open(fname, 'w+')
csv = csv.writer( fp )

# Allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print "Camera is warming up..."
time.sleep(conf["camera_warmup_time"])

# Begin main loop
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
totalCounter = 0
top_rows_to_cut = 90
captureImage = False;
lastRecalibrated = datetime.datetime.now()
ts = timestamp.strftime("%X %x")

# Capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# Grab the raw NumPy array representing the image
	frame = f.array
	timestamp = datetime.datetime.now()
	text = "Nothing Detected" # default unless otherwise

	if captureImage is True:
    		totalCounter += 1

		timestr = time.strftime("%Y%m%d_%H%M%S_")
		print timestr
		t = time.localtime().tm_hour
		ms = round(10*(time.time() - int(time.time())))
		timestr += str(int(ms))

		usbfname = ""
		raspfname = ""
		# Do different things if it's day or night
		if t >= 17 or t < 7:
			# Night time
			raspfname = pictures_dir + 'raspicam_night_{}.jpg'.format(timestr)
			print "RASP: " + raspfname
			cv2.imwrite(raspfname,cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY))
			#call(["fswebcam","-r","640x360","-d","/dev/video0","--no-banner","/home/pi/Src/Python/VT_Video_Tracking/Pictures/usbcam2_{}.jpg".format(timestr)])
			time.sleep(0.02)
			usbfname =  "%susbcam1_night_%s.jpg" % (pictures_dir,timestr)
			print "USB: " + usbfname
			call(["fswebcam","-r","640x360","-d","/dev/video0","--no-banner",usbfname])
			# The following is a work-around for a problem with the USB camera: Sometimes it produces all-black images.
			# The following code looks for very small files (indicating that nothing was recorded) and deletes them
			# to save you the hassle.
	  		if (os.path.getsize(raspfname) < 17000):
				# This suggests an error- an all black image.
				csv.writerow([ts,-1,-1,raspfname])
				os.remove(raspfname)
	  		if (os.path.getsize(usbfname) < 17000):
				# This suggests an error- an all black image.
				csv.writerow([ts,-1,-1,usbfname])
				os.remove(usbfname)

		else:
			# Day time: Toggle between the two cameral (you can't do both at once - does not work welll for reasons I do not comprehend
			
			raspfname = pictures_dir + 'raspicam_day_{}.jpg'.format(timestr)
			cv2.imwrite(raspfname,frame)
	  		if (os.path.getsize(raspfname) < 17000):
				# This suggests an error- an all black image.
				csv.writerow([ts,-1,-1,raspfname])
				os.remove(raspfname)
			# usbfname = pictures_dir + "/usbcam1_day{}.jpg".format(timestr)
			#call(["fswebcam","-r","1280x720","-d","/dev/video0","--no-banner",usbfname]) # this MAY (or may not) cause the pi to crash randomly if during the day - maybe the wind and catching too many things?
			#if toggle_camera == 0:
			#	call(["fswebcam","-r","1280x720","-d","/dev/video0","--no-banner","/home/pi/Src/Python/VT_Video_Tracking/Pictures/usbcam1_{}.jpg".format(timestr)])
			#	toggle_camera = 1
			#else:
			# THIS fails during the day - it gets waaay over saturated. I tried some config settings but have not figured it out. Also, it randomly produces blank photos as well.
			#	call(["fswebcam","-r","1280x720","-d","/dev/video1","-set", "brightness=20%","--no-banner","/home/pi/Src/Python/VT_Video_Tracking/Pictures/usbcam2_{}.jpg".format(timestr)])
			#	toggle_camera = 0

		if (totalCounter % 10 == 0):
			# This file is useful as it is the image used to detect motion (after blurring and cropping)
			cv2.imwrite(pictures_dir + 'gray.jpg'.format(timestr),oldgray)

		captureImage = False # reset the detection 
	
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (31, 25), 0)
	gray[0:top_rows_to_cut,:] = 0
	oldgray = gray
	# if the average frame is None, initialize it
	if avg is None:
		print "starting background model..."
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# loop over the contours
	cont_area = -1
	for c in cnts:
		# if the contour is too small or too big, ignore it
		cont_area = cv2.contourArea(c)
		if cont_area < conf["min_area"] or cont_area > conf["max_area"]:
                        print "%s skip bc area is %d " % (ts, cont_area)
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Movement"
    		# Capture a picture.
    		captureImage = True

	# draw the text and timestamp on the frame (I don't do this as I find it annoying so commented out)
	ts = timestamp.strftime("%X %x")
	#cv2.putText(frame, "Detection Status: {}".format(text), (10, 20),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	#cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
	#	0.35, (0, 0, 255), 1)
	
	if cont_area > 0:
		# Write to a csv file for tracking thresholds for undetected subthreshold events. Usefull for optimizing.
		mn = thresh_buffer.mean(axis = 0)
		csv.writerow([ts,cont_area,mn[0],text])
		thresh_buffer[thresh_buffer_count] = cont_area
		thresh_buffer_count = thresh_buffer_count + 1
		if thresh_buffer_count >= thresh_buffer_size:
                        thresh_buffer_count = 0
		
	# check to see if the frames should be displayed to screen
	if conf["show_video"]:
		# display the camera feed
		gray[0:20,:] = 0
		cv2.imshow("Bobcat Camera", gray)

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

fp.close()
