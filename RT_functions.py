#!/usr/bin/python3
#filename=functions.py


def login_open_sheet(email, password, spreadsheet):
	"""This function is only used when RasPi is online to update logs to 
	google spreadsheet.
	"""
	global worksheet
	#Connect to google docs spreadsheet and return worksheet
	try:
		gc = gspread.login(email, password)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except:
		print('Unable to login and get spreadsheet. Check email, password spreadsheet name.')
		sys.exit(1)

def Start_timer(channel): 
	"""If start signal received, time is saved and event for stop signal
	is created. Start signal event is removed.
	"""
	global starttime
	global SomeoneDriving
	starttime=time.time()
	print("Start")
	GPIO.add_event_detect(PinBarrierRight, GPIO.FALLING, callback=Stop_timer, bouncetime=200)
	if debugging:
		print('STOP detection running')
	GPIO.remove_event_detect(PinBarrierStart) #stop start detection
	if debugging:
		print('START detection terminated')
	#GPIO.remove_event_detect(XX) #stop delete detection
	if debugging:
		print('Detection of delete button stopped.')
	#switch traffic light from green to red
	GPIO.output(PinGreen, 0) #green off
	GPIO.output(PinRed, 1) #red on
	SomeoneDriving=True

def Stop_timer(channel): #Stops timer and evaluates results
	"""A stop signal is received -> save elapsed time to list of elapsed
	times, reset stop detection and clear for next start.
	"""
	global starttime
	global worksheet
	global GDOCS_EMAIL
	global GDOCS_PASSWORD
	global GDOCS_SPREADSHEET_NAME
	global Driver
	global SomeoneDriving
	if debugging:
		print('Stop detected')
	print("Stop")
	elapsedtime=time.time()-starttime
	if debugging:
		print("Dauer (raw): ", elapsedtime)
	minutes=int(elapsedtime/60)
	seconds=int(elapsedtime-minutes*60)
	tseconds=int((elapsedtime-minutes*60-seconds)*1000)
	timestring=('%02d:%02d:%03d' % (minutes, seconds, tseconds))
	timestring_gdoc=('%02d %02d %03d' % (minutes, seconds, tseconds))
	print("Dauer: ", timestring)
	#Save time and driver info to log file
	f=open(logfile, 'a')
	filestring=str(datetime.datetime.now()) + ',' + Track + ',' + Driver + ',' + str(CarNumber) + ',' + Car + ',' + str(Lap) + ',' + str(elapsedtime) + ',' + timestring + '\n'
	if debugging:
		print(filestring)
	f.write(filestring)
	f.close()
	#Append driver and elapsed time to List for evaluation:
	List_of_etimes.append([Driver,elapsedtime])
	#If raspberry is online, same info is written to google-spreadsheet
	if online:
		if worksheet is None:
			worksheet=login_open_sheet(GDOCS_EMAIL, GDOCS_PASSWORD, GDOCS_SPREADSHEET_NAME)
			if debugging:            
				print("Worksheet opened {0}".format(worksheet))
			try:
				worksheet.append_row((datetime.datetime.now(), Track, Driver, CarNumber, Car, Lap, elapsedtime, timestring_gdoc))
			except:
				print('Append error, please try again')
				worksheet=None
	#Reset driver
	Driver=str()
	#Remove event for stop detection
	GPIO.remove_event_detect(PinBarrierRight)
	if debugging:
		print('Terminated STOP detection.')
	#Switch on detection for delete button:
#	GPIO.add_event_detect(XX, GPIO.RISING, callback=delete_last_lap, bouncetime=200)
	if debugging:
		print('Detection of delete button started.')

	SomeoneDriving=False
def detect():  #Scans and evaluates QR-code
	"""detects qr-code from camera and returns string.
	String is shortened from 'QR-Code: ' and linefeed.
	"""
	if debugging:
		print('Start scanning')
	#Make it bright
	GPIO.output(PinWhite, 1)
	#Detection with full resolution image (ca 2.5 MB):
	#subprocess.call(["raspistill -n -t 1 -o cam.png"], shell=True)

	#Detection with lower resolution image (ca 500 kB):
	subprocess.call(["raspistill -n -t 1 -w 1024 -h 1024 -o cam.png"], shell=True)
	#switch off the light:
	GPIO.output(PinWhite, 0)
	#Evaluate picture:
	process=subprocess.Popen(["zbarimg -D -q cam.png"], stdout=subprocess.PIPE, shell=True)
	(out, err)=process.communicate()
		
	qr_code=None
	#'out' looks like "QR-code: TextOfCodeHere\n" and is a byte object.
	# Make String object and remove unnecessary characters:
	if debugging:
		print(out)
	outstr=str(out)
	if debugging:
		print('outstr: ' + outstr)
	if pyversion==3:
		if len(outstr)>10:
			qr_code=outstr[10:-3]
	elif pyversion==2:
		if len(outstr)>8:
			qr_code=outstr[8:]
	if qr_code[-1:]=="\n":   #new 2014-10-20: Test for new line at end of string
		qr_code=qr_code[:-1]
	return qr_code

def delete_last_lap(): #deletes last recorded lap from memory and file
	"""If user decides last elapsed time was invalid, this function
	deletes the last recorded time from the list of elapsed times.
	"""
	global List_of_etimes
	List_of_etimes=List_of_etimes[:-1] #delete last tuple in list of elapsed times
	if debugging:
		print('Last entry in list of elapsed times was deleted.')
	#write to file that last lap is deleted:
	f=open(logfile, 'a')
	filestr='Previous Lap is considered invalid.'
	f.write(filestr)

