class Effect:
	def __init__(self, name):
		self.name = name
		self.enabled = False
		
	def __str__(self):
		return f"{self.name}"
	
	def toggleEnable(self, enable):
		self.enabled = enable
		
	def getEnable(self):
		return self.enabled

	def getName(self):
		return self.name
