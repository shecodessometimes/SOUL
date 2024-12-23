import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD  # Ensure you're using the GPIO version of CharLCD
from Effect import Effect
from AudioManager import AudioManager
class LCDManager:
	def __init__(self, next_b_pin, select_b_pin, rs_pin, en_pin, data_1_pin, data_2_pin, data_3_pin, data_4_pin):
		# Set GPIO numbering mode to BOARD or BCM
		GPIO.setmode(GPIO.BOARD)  # Use GPIO.BCM if you are using BCM numbering

		# Initialize the LCD (using 4-bit mode) and specify the numbering_mode
		self.lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
		self.lcd.cursor_mode = 'blink'
		
		print("Successfully initialized the LCDManager")
		
	def __str__(self):
		return f"<LCDManager object>"
	
	def writeLCDLine(self, lines_array, line_num, audio_manager):
		top_line = line_num
		if line_num % 2 == 1:
			top_line = line_num - 1
		
		# Redraw array
		self.lcd.clear()
		for i in range(2):
			self.lcd.cursor_pos = (i,0)
			effect = lines_array[top_line + i]
			if audio_manager.isEffect(effect):
				effect_obj = audio_manager.getEffectObj(effect)
				if effect_obj.getEnable():
					line = self.neatLine(effect, 'on')
				else:
					line = self.neatLine(effect, 'off')
			else:
				line = effect
			self.lcd.write_string(line)
		
		self.lcd.cursor_pos = ((line_num % 2),0)
	
	def setHello(self):
		# Write "Hello world!" to the second row, fourth column
		self.lcd.cursor_pos = (0,0)  # Row 1 (second row), column 3 (fourth character position)
		self.lcd.write_string(u'Welcome to SOUL!')
		self.lcd.cursor_pos = (1,0)  # Row 1 (second row), column 3 (fourth character position)
		self.lcd.write_string(u'hi :)')
	
	def neatLine(self, item1, item2):
		char_nums = 16
		neat_line = str(item1) + ' '*(char_nums - len(item1) - len(str(item2))) + str(item2)
		return neat_line[:char_nums]
	
	def cleanGPIO(self):
		GPIO.cleanup()
