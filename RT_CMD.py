#!/usr/bin/python3
#filename=RT_CMD.py

"""Command Line utility for rally timer. Requires module 'functions.py'."""
#small change

import RPi.GPIO as GPIO
import time, datetime, gspread, sys, os, subprocess
from operator import itemgetter
import RT_functions
Version=001

"""Phototransistor for Start on GPIO 24, for Finish on 23.
GPIO 18 controls additional light to enhance readability of QR-Codes.
Process: Drive Car on Start-ramp -> Read QR-Code with driver and Car
Information -> light-barrier for start actice -> when released, save
start time and block light barrier for start, enable light-barrier for
finish -> light barrier finish released -> calculate elapsed time and
save with driver, Track and Car info to log file and spreadsheet
"""

"""Button to delete last stopped Lap as long as next driver did not start
yet: GPIO XX"""

#Check wich version of python is running:
pyversion=int(sys.version[:1])

#Login for Google-Spreadsheet:
GDOCS_EMAIL = 'dasimme@gmail.com'
GDOCS_PASSWORD = 'rjjmdlvqkvsvupwk'
GDOCS_SPREADSHEET_NAME = 'Rallye-Meisterschaft'

#Set true for debugging
debugging=True
#Set true to upload data to google-spreadsheet:
online=False

Track=str()
Driver=str()
NextDriver=str()
CarNumber=int()
NextCarNumber=int()
Car=str()
NextCar=str()
Lap=int()
starttime=0.0
working_dir='/home/simme/Rallye/'
MaxLaps=5
CountingLaps=3
SomeoneDriving=False

# Set GPIO-pins:
PinGreen=25 #Green traffic light on GPIO Pin 25
PinYellow=27 #Yellow traffic light on GPIO Pin 27
PinRed=22 #Red traffic light on GPIO Pin 22
PinWhite=18 #White LED for QR-Code reading on Pin 18
PinWhiteMaxBrightness=50 #Maximum brightness for white LED PWM
PinBarrierRight=23 #Light barrier finish on right side (fototransistor)
PinBarrierLeft=0 #Light barrier finish on right side (fototransistor)
PinBarrierStart=24 #Light barrier start (fototransistor)
PinResetLap=0 #Button to delete last lap

GPIO.setmode(GPIO.BCM)
GPIO.setup(PinWhite, GPIO.OUT, initial=0) #LEDs for QR-Code reading
GPIO.setup(PinBarrierStart, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Light barrier start
GPIO.setup(PinBarrierRight, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Light barrier finish
GPIO.setup(PinGreen, GPIO.OUT, initial=0) #Green light (Startampel)
GPIO.setup(PinYellow, GPIO.OUT, initial=0) #Yellow light (Startampel)
GPIO.setup(PinRed, GPIO.OUT, initial=0) #Red light (Startampel)
#GPIO.setup(PinResetLap, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Button to delete last lap

worksheet = None
starttime = None

#Welcome:
os.system('clear')
print('----------------------------------------------')
print('         Welcome to Simmes RC-Rallyetimer     ')
print('----------------------------------------------')

if debugging:
	print('Running on Python version:' + str(pyversion))
#Make a directory for files:
notrack=True
print('Enter date and track name e.g. 2014-01-31_Fancytrack')
while notrack:
	try:
		if pyversion == 3:
			Track=input('Name of current track: ')
		elif pyversion == 2:
			Track=raw_input('Name of current track: ')
		Track_dir=working_dir+'Championships/'+Track
		os.system('mkdir '+Track_dir)
		notrack=False
	except:
		notrack=True
		print('Could not create directory for track, try again.')
logfile=Track_dir+'/logfile.txt'
resultfile=Track_dir+'/results.txt'
List_of_etimes=list()
List_of_Drivers=list()

#Start main loop
print('Drive onto ramp to start timing!')
GPIO.output(PinRed, 1) #Switch on red traffic light

try:
	while True: 
		#If no info for next driver available, try to read QR-Code
		if len(NextDriver)<2 and GPIO.input(PinRed)==GPIO.HIGH:  #Try to find next driver
			try:
				Info_String=RT_functions.detect(debugging, PinWhite, pyversion)
				if len(Info_String)>2:
					#QR-Code read successful, split into strings
					#for further processing
					if debugging:
						print(Info_String)
					Info_List=Info_String.split(",")
					NextDriver=Info_List[1]
					if debugging:
						print('Next driver: '+NextDriver+' scanned.')
					NextCarNumber=int(Info_List[0])
					NextCar=Info_List[2]
					print('Next driver: ' + NextDriver)
					#switch traffic light from red to yellow
					GPIO.output(PinRed, 0) #red off
					GPIO.output(PinYellow, 1) #yellow on
			except:
				if debugging:
					print('Error: ', sys.exc_info()[0])
					print('Failed scanning for Next Driver.')
				time.sleep(3)       
		if len(Driver)<2 and len(NextDriver)>2:   #update current driver with next
			#Next driver found, switch variables:
			Driver=NextDriver
			CarNumber=NextCarNumber
			Car=NextCar
			NextDriver=str()
			NextCarNumber=int()
			NextCar=str()
			#Check for laps driven by driver:
			Lap=1  #if no previous laps found, start with 1st
			for tuple in List_of_etimes:
				if tuple[0]==Driver:
					if debugging:
						print 'Lap of driver found'
					Lap+=1  #increase Lap count
			if Lap==1:  #New driver, add to list
				List_of_Drivers.append(Driver)	
			#Show new screen while ready for start:
			os.system('clear')            
			print('Now driving: '+Driver+', Lap '+str(Lap))
			#Initialize start detection:
			GPIO.add_event_detect(PinBarrierStart, GPIO.FALLING, callback=Start_timer, bouncetime=200)
			if debugging:
				print('Start detection running')
			#switch traffic light from yellow to green
			GPIO.output(PinYellow, 0) #yellow off
			GPIO.output(PinGreen, 1) #green on
			#Wait 6 seconds before scanning for next driver:
			time.sleep(6)
	#End of main loop
except KeyboardInterrupt:  #User interrupt, evaluate results and quit
	GPIO.output(PinWhite, GPIO.LOW) #make sure the lights are switched off
	GPIO.output(PinYellow, 0) #yellow off
	GPIO.output(PinGreen, 0) #green off
	GPIO.output(PinRed, 0) #red off
	GPIO.cleanup() # reset GPIO
	try:     #Evaluate best times and write to results.txt
		Result=sorted(List_of_etimes,key=itemgetter(1))
		if debugging:
			print('Resultfile: '+resultfile)
		f=open(resultfile, 'a')
		os.system('clear')            
		print('Results:')
		totaltimes=list()
		for Driver in List_of_Drivers:
			times=list()
			for ttuple in Result:
				if ttuple[0]==Driver:
					times.append(ttuple[1])
			if len(times)>3:
				times=times[:3]
			filestr='Best 3 times of '+Driver+': '+str(times)
			print(filestr)
			filestr=filestr+'\n'
			f.write(filestr)
			ttime=0
			for splittime in times:
				ttime=ttime+splittime
			totaltimes.append([Driver, ttime])
			filestr='Total of 3 best times: '+str(ttime)
			print(filestr)
			filestr=filestr+'\n'
			f.write(filestr)
		totalresult=sorted(totaltimes,key=itemgetter(1))
		print('Ranking:')
		for ttuple in totalresult:
			ttime=ttuple[1]
			minutes=int(ttime/60)
			seconds=int(ttime-minutes*60)
			tseconds=int((ttime-minutes*60-seconds)*1000)
			timestring=('%02d:%02d:%03d' % (minutes, seconds, tseconds))
			filestr=ttuple[0]+', total: '+timestring
			print(filestring)
			filestr=filestr+'\n'
			f.write(filestr)
			f.write(filestr)
		f.close()
	except:
		print('Something went wrong saving results..')
	print('User interrupt, GPIO cleaned up')
except:  #Something unexpected went terribly wrong here...
	GPIO.output(PinWhite, GPIO.LOW) #make sure the lights are switched off
	GPIO.output(PinYellow, 0) #yellow off
	GPIO.output(PinGreen, 0) #green off
	GPIO.output(PinRed, 0) #red off
	GPIO.cleanup() # reset GPIO
	print('Something went wrong here...')
	if debugging:
		print('Error: ', sys.exc_info()[0])
#End of Program
