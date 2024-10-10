class Effect:
	def __init__(self, name):
		self.name = name
		self.enabled = False
		self.gain = 6
		
		match name:
			case "Chorus":
				self.param_names = ["rate_hz", "depth", "centre_delay_ms", "feedback", "mix"]
				self.param_values = [1.0, 0.25, 7.0, 0.0, 0.5]
			case "Delay":
				self.param_names = ["delay_seconds", "feedback", "mix"]
				self.param_values = [0.5, 0.0, 0.5]
			case "Reverb":
				self.param_names = ["room_size", "damping", "wet_level", "dry_level", "width", "freeze_mode"]
				self.param_values = [0.5, 0.5, 0.33, 0.4, 1.0, 0.0]
		
	def __str__(self):
		return f"{self.name}"
	
	def setEnable(self, new_enable):
		self.enabled = new_enable
		
	def getEnable(self):
		return self.enabled

	def getName(self):
		return self.name

	def getParamNames(self):
		return self.param_names

	def getParamNameAt(self, i):
		return self.param_names[i]

	def getParamValueAt(self, i):
		return self.param_values[i]
		
