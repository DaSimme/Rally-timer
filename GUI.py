#!/usr/bin/python3
#filename=GUI.py

"""GUI for Rally-tool. Requires module 'functions.py'."""

import RPi.GPIO as GPIO
import time, datetime, gspread, sys, os, subprocess
from operator import itemgetter
from RT_functions import *
from tkinter import *

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
debugging=False
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
#GPIO.setup(XX, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Button to delete last lap

worksheet = None

