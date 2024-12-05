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
		self.menu_num
		self.in_menu
		self.menu_array = [effect.getName() for effect in audio_manager.getEffectsArray()]
		self.menu_array.append("Try sine wave")
		self.menu_array.append("Try music")
		self.menu_array.append("IO Devices")
		## if menu_array has an odd number of items, hahaha, it doesn't :)
		#if len(menu_array) % 2 == 1:
		#	menu_array.append("")

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
					in_menu = True
				print('Menu number: ' + str(self.menu_num))
					
				writeLCDLine(self.menu_array, self.menu_num)
			case "modify":
				self.modify_num = self.modify_num + 1
				if self.modify_num >= len(self.modify_array):
					self.modify_num = 0
				self.lcd_manager.writeLCDLine(self.modify_array, self.modify_num)
				
	def selectItemState(self):
		match self.current_state:
			case "menu":
				effect = self.menu_array[self.menu_num]
				if isEffect(effect):
					changeState("modify", effect) # Change the state
				elif effect == "Try sine wave":
					self.audio_manager.applyEffects("sine.wav", effects_board)
				elif effect == "Try music":
					self.audio_manager.applyEffects("emily.wav", effects_board)
				elif effect == "IO Devices":
					changeState("modify", "io")
				else:
					print("In else! Yay!")
					#play effect
			case "modify":
				global modify_array
				match modify_array[modify_num]:
					case "enabled":
						effects_array[menu_num].setEnable(False)
						modify_array[modify_num] = "disabled"
						writeLCDLine(modify_array, modify_num)
						updateBoard()
					case "disabled":
						effects_array[menu_num].setEnable(True)
						modify_array[modify_num] = "enabled"
						writeLCDLine(modify_array, modify_num)
						updateBoard()
					case self.lcd_manager.neatLine("Audio stream:", "enabled"):
						audiostream_enabled = False
						stopAudioStream()					
						writeLCDLine(modify_array, modify_num)
						updateBoard()
					case self.lcd_manager.neatLine("Audio stream:", "disabled"):
						audiostream_enabled = True
						startAudioStream()
						writeLCDLine(modify_array, modify_num)
						updateBoard()
					case "quit" | "back":
						changeState("menu", "quit")
						
				# yes, this is an if/then after a case, but it will work.
				print('hi')
				if any(sub in modify_array[modify_num] for sub in effects_array[menu_num].getParamNames()):
					effects_array[menu_num].nextParamValue(modify_num - 2)
					effect = menu_array[menu_num]
					setModify(effect)
					writeLCDLine(modify_array, modify_num)
					updateBoard()
					print('updated value')
				else:
					print('no sub found')
					
	def changeState(self, new_state, info_str):
		self.current_state = new_state
		match self.current_state:
			case "hello":
				setHello()
			case "menu":
				self.in_menu = True
				setMenu()
			case "modify":
				self.in_menu = False
				setModify(info_str)
				
	def setHello(self):
		# Write "Hello world!" to the second row, fourth column
		lcd.cursor_pos = (0,0)  # Row 1 (second row), column 3 (fourth character position)
		lcd.write_string(u'Welcome to SOUL!')
		lcd.cursor_pos = (1,0)  # Row 1 (second row), column 3 (fourth character position)
		lcd.write_string(u'hi :)')
				
	def setMenu(self):
		# Reset menu number
		menu_num = 0
		
		print('Menu number: ' + str(self.menu_num))
			
		# Update LCD
		self.LCDManager.writeLCDLine(self.menu_array, 0)

	def setModify(self, effect_name):
		if effect_name == "io":
			self.modify_array = []
			self.modify_array.append("Modify Audio I/O")
			in_dev = input_devices[input_devices_i]		
			modify_array.append(self.lcd_manager.neatLine('in', in_dev))
			out_dev = output_devices[output_devices_i]		
			modify_array.append(self.lcd_manager.neatLine('out', out_dev))
			
			# enable/disable audiostream
			if audiostream_enabled:
				modify_array.append(self.lcd_manager.neatLine("Audio stream:", "enabled"))
			else:
				modify_array.append(self.lcd_manager.self.lcd_manager.neatLine("Audio stream:", "disabled"))
			
			# quit
			modify_array.append("back")
			if param_num % 2 == 0:
				modify_array.append("")
				
		else:
			# Find the effects object
			effect_obj = getEffectObj(effect_name)
			
			# Update the modify_array (will be displayed on LCD)
			modify_array = []
			modify_array.append("Modify " + effect_obj.getName())
			if effect_obj.getEnable():
				modify_array.append("enabled")
			else:
				modify_array.append("disabled")
			
			# Write all possible parameter names and values
			param_num = len(effect_obj.getParamNames())
			
			for i in range(param_num):
				param_name = effect_obj.getParamNameAt(i)
				param_val = effect_obj.getParamValueAt(i)
				modify_array.append(neatLine(param_name, param_val))
			
			modify_array.append("back")
			if param_num % 2 == 0:
				modify_array.append("")
		
		# Update LCD
		writeLCDLine(modify_array, 0)
