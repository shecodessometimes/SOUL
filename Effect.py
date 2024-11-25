class Effect:
	def __init__(self, name):
		self.name = name
		self.enabled = False
		self.gain = 6
		
		mix_arr = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
		fed_arr = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
		sec_arr = [0.1, 0.3, 0.5, 0.7, 1.0, 3.0, 5.0, 7.0, 9.0, 10.0, 15.0]
		dbn_arr = [-24, -12, -9, -6, -3, -2, -1, -0.5]
		
		match name:
			case "Chorus":
				self.param_names = ["rate_hz", "depth", "centre_delay_ms", "feedback", "mix"]
				self.param_values = [sec_arr, mix_arr, sec_arr, fed_arr, mix_arr]
				self.param_indices = [1, 1, 5, 1, 2]
			case "Delay":
				self.param_names = ["delay_seconds", "feedback", "mix"]
				self.param_values = [sec_arr, fed_arr, mix_arr]
				self.param_indices = [2, 0, 5]
			case "Reverb":
				self.param_names = ["room_size", "damping", "wet_level", "dry_level", "width"]
				self.param_values = [sec_arr, mix_arr, mix_arr, mix_arr, mix_arr]
				self.param_indices = [2, 5, 4, 4, 0]
			case "Compressor":
				self.param_names = ["threshold_db", "ratio"]
				self.param_values = [dbn_arr, sec_arr]
				self.param_indices = [4, 5]
		
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

	def nextParamValue(self, i):		
		print('parameter: ')
		print(self.param_names[i])
		print('parameter: ')
		print(self.param_values[i])
		print('parameter index: ')
		print(self.param_indices[i])
		val_arr = self.param_values[i]
		val_idx = self.param_indices[i]
		
		val_idx = val_idx + 1
		
		if val_idx > (len(val_arr) - 1):
			val_idx = 0
			
		self.param_indices[i] = val_idx
		print('parameter: ')
		print(self.param_values[i])
		print('parameter index: ')
		print(self.param_indices[i])
		

	def getParamValueAt(self, i):
		val_arr = self.param_values[i]
		val_idx = self.param_indices[i]
		print(f'val_arr: {val_arr}')
		print(f'val_idx: {val_idx}')
		print(f'i: {i}')
		print(f'val_arr[val_idx]: {val_arr[val_idx]}')
		return val_arr[val_idx]
		
