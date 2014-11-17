
from tkinter import *
from tkinter.ttk import *
import RPi.GPIO as GPIO
import os

debugging=True
online=False
homedir="/home/simme/Rallye/Championships/"
Driver_File='/home/simme/Rallye/Drivers/ListOfDrivers.txt'
# Set GPIO-pins:
PinGreen=25 #Green traffic light on GPIO Pin 25
PinYellow=27 #Yellow traffic light on GPIO Pin 27
PinRed=22 #Red traffic light on GPIO Pin 22
PinWhite=18 #White LED for QR-Code reading on Pin 18
PinBarrierRight=23 #Light barrier finish on right side (fototransistor)
PinBarrierLeft=0 #Light barrier finish on right side (fototransistor)
PinBarrierStart=24 #Light barrier start (fototransistor)
PinResetLap=0 #Button to delete last lap
PinLaserStart=8 #Control Laser for start barrier

class LED(Frame):
	"""A tkinter LED widged based on http://codepad.org/hXiu1ZeW
	a = LED(root, 10)
	a.set(True)
	current_state = a.get()
	"""
	OFF_STATE = 0
	ON_STATE=1
	
	def __init__(self,master,size=10,**kw):
		self.size=size
		Frame.__init__(self,master,width=size,height=size)
		self.configure(**kw)
		self.state=LED.OFF_STATE
		self.c=Canvas(self,width=self['width'],height=self['height'])
		self.c.grid()
		self.led=self._drawcircle((self.size/2)+1,(self.size/2)+1,(self.size-1)/2)
	def _drawcircle(self,x,y,rad):
		"""Draws the circle initially"""
		color="red"
		return self.c.create_oval(x-rad,y-rad,x+rad,y+rad,width=rad/5,fill=color,outline='black')
	def _change_color(self):
		"""Updates the LED color"""
		if self.state == LED.ON_STATE:
			color="green"
		else:
			color="red"
		self.c.itemconfig(self.led, fill=color)
	def set(self,state):
		"""Set the state of the LED to be true or false"""
		self.state=state
		self._change_color()
	def get(self):
		"""Returns the current state of the LED"""
		return self.state

class ttkLaptimer():
  
	def __init__(self, root):


		self.init_GPIO()
		self.init_variables()
		self.build_GUI()

		
		
		
	def init_GPIO(self):
		#Initialize GPIO Pins:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(PinWhite, GPIO.OUT, initial=0) #LEDs for QR-Code reading
		GPIO.setup(PinBarrierStart, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Light barrier start
		GPIO.setup(PinBarrierRight, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Light barrier finish
		GPIO.setup(PinGreen, GPIO.OUT, initial=0) #Green light (Startampel)
		GPIO.setup(PinYellow, GPIO.OUT, initial=0) #Yellow light (Startampel)
		GPIO.setup(PinRed, GPIO.OUT, initial=0) #Red light (Startampel)
		GPIO.setup(PinLaserStart, GPIO.OUT, initial=0)
		#GPIO.setup(PinResetLap, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Button to delete last lap
	def init_variables(self):
		#Initialize Variables:
		self.selected_Championship=StringVar()
		self.selected_Rallye=StringVar()
		self.selected_Stage=StringVar()
		self.selected_Championship="Test-Rallye"
		self.Track=str()
		self.Driver=str()
		self.NextDriver=str()
		self.CarNumber=int()
		self.NextCarNumber=int()
		self.Car=str()
		self.NextCar=str()
		self.Lap=int()
		self.starttime=0.0
		self.working_dir='/home/simme/Rallye/'
		self.MaxLaps=5
		self.CountingLaps=3
		self.List_of_etimes=list()
		self.List_of_Drivers=list()

		
	def build_GUI(self):
		#Notebook
		self.frame = Frame(root)
		self.notebook = Notebook(self.frame)
		
		#Hardware Setup Page
		f1=Frame(self.notebook, width=400, height=400)
		self.notebook.add(f1, text='Setup')
		RedButton=Button(f1, text="Red", command=self.toggle_red).grid(row=0, column=0, sticky=(N, S, E, W))
		YellowButton=Button(f1, text="Yellow", command=self.toggle_yellow).grid(row=1, column=0, sticky=(N, S, E, W))
		GreenButton=Button(f1, text="Green", command=self.toggle_green).grid(row=2, column=0, sticky=(N, S, E, W))
		WhiteButton=Button(f1, text="White", command=self.toggle_white).grid(row=0, column=1, sticky=(N, S, E, W))
		LaserStartButton=Button(f1, text="Laser Start", command=self.toggle_laser_start).grid(row=0, column=2, sticky=(N, S, E, W))
		#self.led = LED(self,20)
		#self.led.grid(row=1,column=2)
		
		#Rally Info Page
		f2=Frame(self.notebook, width=400, height=400) 
		self.notebook.add(f2, text='Rally Info')
		rallylabel=Label(f2, text="Select or create new Rally:").grid(row=0, column=0, sticky=(N, S, E, W))
		self.list_rally = StringVar()
		strral=self.working_dir+'Championships/'
		list_rally = os.listdir(strral)
		if debugging:
			print('Loaded List of Rallys: '+str(list_rally))
		self.RaCoVar=StringVar() #Variable for combobox
		rally_select=Combobox(f2, textvariable=self.RaCoVar, values=list_rally, width=30).grid(row=1, column=0, sticky=(N, S, E, W))
		if debugging:
			print(self.RaCoVar)
		#self.rally_select.bind('<<ComboboxSelected>>', self.rally_choosen)
		SelectRallyButton=Button(f2, text="Select", command=self.select_rally).grid(row=1, column=1, sticky=(N, S, E, W))
		
		#Split Info Page
		f3=Frame(self.notebook, width=400, height=400) 
		self.notebook.add(f3, text='Split Info')
		
		#Split timing page
		f4=Frame(self.notebook, width=400, height=400) 
		self.notebook.add(f4, text='Split timing')
		self.Driverlabel=Label(f4, text="Now Driving: "+self.Driver).grid(row=0, column=0, sticky=(N, S, E, W))
		self.ElapsedLabel=Label(f4, text="Elapsed time: ").grid(row=1,column=0,sticky=(N, S, E, W))
		self.StartButton=Button(f4, text="Start", command=self.start_split).grid(row=0, column=2, sticky=(N, S, E, W))
		self.StopButton=Button(f4, text="Stop", command=self.stop_split).grid(row=1, column=2, sticky=(N, S, E, W))
		
		f=open(Driver_File, 'r')
		List_of_drivers=[] #Create empty lists for data
		List_of_numbers=[]
		List_of_cars=[]
		for line in f:
			tup=line.split(',')
			List_of_numbers.append(tup[0])
			List_of_drivers.append(tup[1])
			List_of_cars.append(tup[2])
		if debugging:
			print(List_of_drivers)

		self.Display_Championship(f2)
    
		#self.Combo_track_select(f2)
		#Layout
		self.frame.grid(row=0, column=0, sticky=(N, S, E, W))
		self.notebook.grid(row=0, column=0, sticky=(N, S, E, W))
		#Resize rules
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		self.frame.columnconfigure(0, weight=2)
		self.frame.rowconfigure(0, weight=2)
		#Menubar
		menubar = Menu(root)
		root['menu'] = menubar
		menu_file = Menu(menubar, tearoff=0)
		menu_file.add_command(label="Open Championship", command=self.Open_Championship)
		menu_file.add_command(label="Open Rally", command=self.Open_Rally, state=DISABLED)
		menu_file.add_command(label="Open Stage", command=self.Open_Stage, state=DISABLED)
		menu_file.add_separator()
		menu_file.add_command(label="New Championship", command=self.New_Championship)
		menu_file.add_command(label="New Rally", command=self.New_Rally, state=DISABLED)
		menu_file.add_command(label="New Stage", command=self.New_Stage, state=DISABLED)
		menu_file.add_separator()
		menu_file.add_command(label="Quit", command=self.quit)
		menubar.add_cascade(menu=menu_file, label='File')
		drivermenu = Menu(menubar, tearoff=0)
		drivermenu.add_command(label="View Driver", command=self.View_Driver)
		drivermenu.add_command(label="Edit Driver", command=self.Edit_Driver)
		drivermenu.add_command(label="New Driver", command=self.New_Driver)
		menubar.add_cascade(label="Driver", menu=drivermenu)
		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="About", command=self.About)
		helpmenu.add_command(label="Help Index", command=self.Help_Index)
		menubar.add_cascade(label="Help", menu=helpmenu)
		
	def toggle_red(self): #toggles red LED
		if GPIO.input(PinRed):
			GPIO.output(PinRed, 0)
		else:
			GPIO.output(PinRed, 1)
			
	def toggle_yellow(self): #toggles yellow LED
		if GPIO.input(PinYellow):
			GPIO.output(PinYellow, 0)
		else:
			GPIO.output(PinYellow, 1)
			
	def toggle_green(self): #toggles green LED
		if GPIO.input(PinGreen):
			GPIO.output(PinGreen, 0)
		else:
			GPIO.output(PinGreen, 1)
			
	def toggle_white(self): #toggles white LED
		if GPIO.input(PinWhite):
			GPIO.output(PinWhite, 0)
		else:
			GPIO.output(PinWhite, 1)
			
	def toggle_laser_start(self): #toggle Laser for start
		if GPIO.input(PinLaserStart):
			GPIO.output(PinLaserStart, 0)
		else:
			GPIO.output(PinLaserStart, 1)
		
	def rally_choosen(self):
		"""New rally choosen in combobox"""
		if debugging:
			print('New rally choosen in combobox.')
			
	def select_rally(self):
		"""Creates a new directory for new rally or takes existing one
			and sets Track String to current rally"""
		self.Track=str(self.RaCoVar)
		if debugging:
			print('Track variable: '+self.Track)
			
	def start_split(self):
		"""starts the process of timing and blocks all other functions"""
		if debugging:
			print('StartButton pressed')
		self.notebook.tab(0, state=DISABLED)
		self.notebook.tab(1, state=DISABLED)
		self.notebook.tab(2, state=DISABLED)
		
	def stop_split(self):
		"""stops the process of timing and enables all other functions"""
		if debugging:
			print('StopButton pressed')
		self.notebook.tab(0, state=NORMAL)
		self.notebook.tab(1, state=NORMAL)
		self.notebook.tab(2, state=NORMAL)
		

	def Open_Championship(self):
		#bestehende Rennserie oeffnen
		if debugging == 1:
			print('Open Championship')

	def Open_Rally(self):
		#bestehende Rallye fortfuehren
		if debugging == 1:
			print('Open Rally')
                          
	def Open_Stage(self):
		#Bestehende Etappe oeffnen
		if debugging == 1:
			print('Open Stage')

	def New_Championship(self):
		#Neue Rennserie anlegen
		if debugging == 1:
			print('New Championship')

	def New_Rally(self):
		#Neue Rallye anlegen
		if debugging == 1:
			print('New Rally')

	def New_Stage(self):
		#Neue Etappe anlegen
		if debugging == 1:
			print('New Stage')

	def View_Driver(self):
		#Fahrerinformationen anzeigen
		if debugging == 1:
			print('View Driver')

	def Edit_Driver(self):
		#Fahrerinformationen aendern
		if debugging == 1:
			print('Edit Driver')

	def New_Driver(self):
		#Neuen Fahrer anlegen
		if debugging == 1:
			print('New Driver')

	def About(self):
		#Info zum Programm anzeigen
		if debugging == 1:
			print('About')

	def Help_Index(self):
		#Hilfe anzeigen
		if debugging == 1:
			print('Help Index')
      
	def quit(self):
		GPIO.cleanup() # reset GPIO
		root.destroy()

	def Display_Championship(self, parent):
		ctext='dummy'
		#  ttk.Label(parent, ctext).grid(column=1, row=1, sticky=N)
		self.txt=Label(parent, textvariable=ctext).grid(column=1, row=1, sticky=N)
    
	#def Combo_track_select(self, parent):
		#  cbv = StringVar()
		#  self.combotr = Combobox(parent, textvariable=cbv, values=('Track 1', 'Track 2', 'Track 3')).pack(side=TOP)
    

if __name__=='__main__':
	root = Tk()
	root.title('Simmes Rally Tool')
	app = ttkLaptimer(root)
	root.mainloop()
  
