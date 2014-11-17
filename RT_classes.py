from operator import itemgetter

class Driver:
	def __init__(self, name):
		self.name=name
		self.car=str()
		self.car_no=int()
		self.laps=list()
		self.best_lap=[]
		
	def add_lap(self, lap, elapsed_time, time_string):
		self.laps.append([lap, elapsed_time, time_string])
		if len(self.best_lap)==0:
			self.best_lap=[lap, elapsed_time, time_string]
		else:
			result=sorted(self.laps,key=itemgetter(1))
			self.best_lap=result[0]
	
	def get_best_lap(self):
		return self.best_lap

		
class Championship:
	def __init__(self, name):
		self.name=name
		self.number_of_rallys=12
		self.rallys_finished=0
		self.rallys=list()
		#[Rank, points result]
		self.point_rules=([1,10],[2,9],[3,8],[4,7],[5,6],[6,5],[7,4],[8,3])
		#Number of points awarded for attending a rally:
		self.min_points_attend=2
		self.table_of_results=list()
		
class Rally:
	def __init__(self, name):
		self.name=name
		self.number_of_stages=0
		self.stages_finished=0
		self.total_length=0
		self.surfaces=list()
		self.date=None
		self.max_laps_per_stage=2
		self.counting_laps_per_stage=1
		
class Stage(self,parent):
	def __init__(self,number):
		self.number=number
		self.length=0
		self.surfaces=list()
		self.weather_temp=0
		self.weather_wind=None
		self.weather_rain=None
		self.weather_snow=None
		self.results=list()
		self.elapsed_times=list()
		self.now_driving=None
		self.last_driver=None
		self.next_driver=None
		self.starttime=0.0
		self.elapsedtime=0.0
		
		