class Effect:
	def __init__(self, name):
		self.name = name
		self.enabled = False
		self.gain = 6
		
	def __str__(self):
		return f"{self.name}"
	
	def toggleEnable(self, enable):
		self.enabled = enable
		
	def getEnable(self):
		return self.enabled

	def getName(self):
		return self.name

	def getGain(self):
		return self.gain

	def setGain(self, new_gain):
		self.gain = new_gain
		
