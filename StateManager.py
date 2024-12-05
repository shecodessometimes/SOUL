from AudioManager import AudioManager
from LCDManager import LCDManager
from IOManager import IOManager
from Effect import Effect

class StateManager:
	def __init__(self, audio_manager, lcd_manager):
		# initialize objects
		self.audio_manager = audio_manager
		self.lcd_manager = lcd_manager
		
		# hello state
		self.state = "hello"
		
		# menu state
		self.menu_num = 0
		self.in_menu = False
		self.menu_array = [effect.getName() for effect in audio_manager.getEffectsArray()]
		self.menu_array.append("Try sine wave")
		self.menu_array.append("Try music")
		self.menu_array.append("IO Devices")
		
		# if self.menu_array has an odd number of items, hahaha, it doesn't :)
		if len(self.menu_array) % 2 == 1:
			self.menu_array.append("")

		# modify state
		self.modify_array = []
		self.modify_num = 0
		
		print("Successfully initialized the StateManager")
		
	def __str__(self):
		return f"<StateManager object>"
	
	def setState(self, new_state):
		self.state = new_state
		
	def getState(self):
		return self.state
		
	def nextItemState(self):
		match self.current_state:
			case "menu":
				# Update menu number
				if self.in_menu:
					self.menu_num = self.menu_num + 1
					if self.menu_num >= len(self.menu_array):
						self.menu_num = 0
				else:
					self.menu_num = 0
					self.in_menu = True
				print('Menu number: ' + str(self.menu_num))
					
				self.lcd_manager.writeLCDLine(self.menu_array, self.menu_num, self.audio_manager)
			case "modify":
				self.modify_num = self.modify_num + 1
				if self.modify_num >= len(self.modify_array):
					self.modify_num = 0
				self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
				
	def selectItemState(self):
		match self.current_state:
			case "menu":
				effect = self.menu_array[self.menu_num]
				if self.audio_manager.isEffect(effect):
					self.changeState("modify", effect) # Change the state
				elif effect == "Try sine wave":
					self.audio_manager.applyEffects("sine.wav")
				elif effect == "Try music":
					self.audio_manager.applyEffects("emily.wav")
				elif effect == "IO Devices":
					self.changeState("modify", "io")
				else:
					print("In else! Yay!")
					#play effect
			case "modify":
				audio_en_str = self.lcd_manager.neatLine("Audio stream:", "enabled")
				audio_dis_str = self.lcd_manager.neatLine("Audio stream:", "disabled")
				match self.modify_array[self.modify_num]:
					case "enabled":
						self.audio_manager.enableDisableEffect(self.menu_num, "disable")
						self.modify_array[self.modify_num] = "disabled"
						self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
						self.audio_manager.updateBoard()
					case "disabled":
						self.audio_manager.enableDisableEffect(self.menu_num, "enable")
						self.modify_array[self.modify_num] = "enabled"
						self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
						self.audio_manager.updateBoard()
					case value if value == audio_en_str:
						audiostream_enabled = False
						stopAudioStream()					
						self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
						self.audio_manager.updateBoard()
					case value if value == audio_dis_str:
						audiostream_enabled = True
						startAudioStream()
						self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
						self.audio_manager.updateBoard()
					case "quit" | "back":
						self.changeState("menu", "quit")
						
				# yes, this is an if/then after a case, but it will work.
				print('hi')
				if self.audio_manager.isEffectParam(self.modify_array[self.modify_num], self.menu_num):
					self.audio_manager.nextEffectParam(self.menu_num, self.modify_num - 2)
					effect = self.menu_array[self.menu_num]
					self.setModify(effect)
					self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num, self.audio_manager)
					self.audio_manager.updateBoard()
					print('updated value')
				else:
					print('no sub found')
					
	def changeState(self, new_state, info_str):
		self.current_state = new_state
		match self.current_state:
			case "hello":
				self.lcd_manager.setHello()
			case "menu":
				self.in_menu = True
				self.setMenu()
			case "modify":
				self.in_menu = False
				self.setModify(info_str)
				
	def setMenu(self):
		# Reset menu number
		self.menu_num = 0
		
		print('Menu number: ' + str(self.menu_num))
			
		# Update LCD
		self.lcd_manager.writeLCDLine(self.menu_array, 0, self.audio_manager)

	def setModify(self, effect_name):
		if effect_name == "io":
			self.modify_array = []
			self.modify_array.append("Modify Audio I/O")
			in_dev = input_devices[input_devices_i]		
			self.modify_array.append(self.lcd_manager.neatLine('in', in_dev))
			out_dev = output_devices[output_devices_i]		
			self.modify_array.append(self.lcd_manager.neatLine('out', out_dev))
			
			# enable/disable audiostream
			if audiostream_enabled:
				self.modify_array.append(self.lcd_manager.neatLine("Audio stream:", "enabled"))
			else:
				self.modify_array.append(self.lcd_manager.self.lcd_manager.neatLine("Audio stream:", "disabled"))
			
			# quit
			self.modify_array.append("back")
			if param_num % 2 == 0:
				self.modify_array.append("")
				
		else:
			# Find the effects object
			effect_obj = self.audio_manager.getEffectObj(effect_name)
			
			# Update the self.modify_array (will be displayed on LCD)
			self.modify_array = []
			self.modify_array.append("Modify " + effect_obj.getName())
			if effect_obj.getEnable():
				self.modify_array.append("enabled")
			else:
				self.modify_array.append("disabled")
			
			# Write all possible parameter names and values
			param_num = len(effect_obj.getParamNames())
			
			for i in range(param_num):
				param_name = effect_obj.getParamNameAt(i)
				param_val = effect_obj.getParamValueAt(i)
				self.modify_array.append(self.lcd_manager.neatLine(param_name, param_val))
			
			self.modify_array.append("back")
			if param_num % 2 == 0:
				self.modify_array.append("")
		
		# Update LCD
		self.lcd_manager.writeLCDLine(self.modify_array, 0, self.audio_manager)
