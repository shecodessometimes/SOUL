import time
from gpiozero import Button
from RPLCD.gpio import CharLCD  # Ensure you're using the GPIO version of CharLCD
import RPi.GPIO as GPIO
from pedalboard import Pedalboard, Compressor, Chorus, Delay, Reverb, load_plugin, Gain
from pedalboard.io import AudioFile
from Effect import Effect
#from playsound import playsound
import pygame
import sounddevice as sd


# Initialize ===========================================================
next_button = Button(2); # next-button connected to GPIO2
select_button = Button(3); # select-button connected to GPIO3

# Set GPIO numbering mode to BOARD or BCM
GPIO.setmode(GPIO.BOARD)  # Use GPIO.BCM if you are using BCM numbering

# Initialize the LCD (using 4-bit mode) and specify the numbering_mode
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
lcd.cursor_mode = 'blink'

# set the current state!
current_state = "hello"
button_pressing = 0

# Create lists
# To definitely do: delay, looping, reverb
# menu_array += [Effect(name) for name in ["Chord", "Crunch", "Delay", "Reverb", "Slowed", "Loop"]]
effects_array = [Effect(name) for name in ["Chorus", "Delay", "Reverb", "Compressor"]]

menu_array = [effect.getName() for effect in effects_array]
menu_array.append("Try sine wave")
menu_array.append("Try music")


modify_array = []
modify_num = 0

effects_board = Pedalboard([
	# Compressor(threshold_db=-50, ratio=25),
	# Compressor(threshold_db=-3, ratio=5),
	])
  
## if menu_array has an odd number of items, hahaha, it doesn't :)
#if len(menu_array) % 2 == 1:
#	menu_array.append("")

# Functions ============================================================
def nextItem():
	global button_pressing
	button_pressing = button_pressing + 1
	if button_pressing == 1:
		match current_state:
			case "menu":
				global menu_num
				global in_menu
				
				# Update menu number
				if in_menu:
					menu_num = menu_num + 1
					if menu_num >= len(menu_array):
						menu_num = 0
				else:
					menu_num = 0
					in_menu = True
				print('Menu number: ' + str(menu_num))
					
				setLCDLine(menu_array, menu_num)
			case "modify":
				global modify_num
				modify_num = modify_num + 1
				if modify_num >= len(modify_array):
					modify_num = 0
				setLCDLine(modify_array, modify_num)
		button_pressing = 0
			
			
def selectItem():
	global button_pressing
	button_pressing = button_pressing + 1
	if button_pressing == 1:
		global current_state
		match current_state:
			case "menu":
				global in_menu
				global menu_num
				effect = menu_array[menu_num]
				if isEffect(effect):
					changeState("modify", effect) # Change the state
				elif effect == "Try sine wave":
					applyEffects("sine.wav", effects_board)
				elif effect == "Try music":
					applyEffects("emily.wav", effects_board)
				else:
					print("In else! Yay!")
					#play effect
			case "modify":
				global modify_array
				match modify_array[modify_num]:
					case "enabled":
						effects_array[menu_num].setEnable(False)
						modify_array[modify_num] = "disabled"
						setLCDLine(modify_array, modify_num)
						updateBoard()
					case "disabled":
						effects_array[menu_num].setEnable(True)
						modify_array[modify_num] = "enabled"
						setLCDLine(modify_array, modify_num)
						updateBoard()
					case "quit" | "back":
						changeState("menu", "quit")
						
				# yes, this is an if/then after a case, but it will work.
				print('hi')
				if any(sub in modify_array[modify_num] for sub in effects_array[menu_num].getParamNames()):
					effects_array[menu_num].nextParamValue(modify_num - 2)
					effect = menu_array[menu_num]
					setModify(effect)
					setLCDLine(modify_array, modify_num)
					updateBoard()
					print('updated value')
				else:
					print('no sub found')
					
		time.sleep(1)
		button_pressing = 0
			
def changeState(state, info_str):
	match state:
		case "hello":
			setHello()
		case "menu":
			setMenu()
		case "modify":
			global current_state
			global in_menu
			current_state = "modify"
			in_menu = False
			
			setModify(info_str)
			
def setHello():
	# Write "Hello world!" to the second row, fourth column
	lcd.cursor_pos = (0,0)  # Row 1 (second row), column 3 (fourth character position)
	lcd.write_string(u'Welcome to SOUL!')
	lcd.cursor_pos = (1,0)  # Row 1 (second row), column 3 (fourth character position)
	lcd.write_string(u'hi :)')
			
def setMenu():
	global menu_num
	global in_menu
	global current_state
	
	# Reset menu number
	menu_num = 0
	in_menu = True
	current_state = "menu"
	
	print('Menu number: ' + str(menu_num))
		
	# Update LCD
	setLCDLine(menu_array, 0)

def setLCDLine(lines_array, line_num):
	top_line = line_num
	if line_num % 2 == 1:
		top_line = line_num - 1
	
	# Redraw array
	lcd.clear()
	for i in range(2):
		lcd.cursor_pos = (i,0)
		effect = lines_array[top_line + i]
		if isEffect(effect):
			effect_obj = getEffectObj(effect)
			if effect_obj.getEnable():
				line = effect + ' '*(14 - len(effect)) + 'on'
			else:
				line = effect + ' '*(13 - len(effect)) + 'off'
		else:
			line = effect
		lcd.write_string(line)
	
	lcd.cursor_pos = ((line_num % 2),0)

def setModify(effect_name):
	# Find the effects object
	effect_obj = getEffectObj(effect_name)
	
	# Update the modify_array (will be displayed on LCD)
	global modify_array
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
		modify_array.append(param_name + ' '*(16 - len(param_name) - len(str(param_val))) + str(param_val))
	
	modify_array.append("back")
	if param_num % 2 == 0:
		modify_array.append("")
	
	# Update LCD
	setLCDLine(modify_array, 0)

def isEffect(effect_name):
	i = 0
	while i < len(effects_array) and effects_array[i].getName() != effect_name:
		i = i + 1
	
	if i >= len(effects_array):
		return False
	else:
		return True
	
def getEffectObj(effect_name):
	i = 0
	while i < len(effects_array) and effects_array[i].getName() != effect_name:
		print(effects_array[i].getName())
		print(effect_name)
		print(i)
		i = i + 1
	
	return effects_array[i]

def updateBoard():
	global effects_board
	effects_board = Pedalboard([
	Gain(gain_db=0),
	])
	
	effect_num = 1
	
	for effect in effects_array:
		if effect.getEnable():
			match effect.getName():
				case "Chorus":
					effects_board.append(Chorus())
				case "Delay":
					effects_board.append(Delay())
				case "Phasor":
					effects_board.append(Phasor())
				case "Reverb":
					effects_board.append(Reverb())
				case "Compressor":
					effects_board.append(Compressor())
			
			for param_i in range(len(effect.getParamNames())):
				param_name = effect.getParamNameAt(param_i)
				param_val = effect.getParamValueAt(param_i)
				effects_board[effect_num]
				exec("effects_board[effect_num]." + param_name + " = " + str(param_val))
			effect_num = effect_num + 1

def applyEffects(audio_file, board):
	samplerate = 44100.0
	with AudioFile(audio_file).resampled_to(samplerate) as f:
		audio_in = f.read(f.frames)
	
	audio_out = board(audio_in, samplerate)
	audio_out_file = audio_file[:audio_file.find('.')] + 'processed-output' + str(time.time()) + '.wav'

	with AudioFile(audio_out_file, 'w', samplerate, audio_out.shape[0]) as f:
		f.write(audio_out)
		
	# for playing note.wav file
	pygame.mixer.init()
	pygame.mixer.music.load(audio_out_file)
	pygame.mixer.music.play()
	# print('playing sound using  playsound')
	# playsound(audio_out_file)
	
	return audio_out
						
# def streamEffects(audioFile):
# 	with AudioStream(
#   		input_device_name="Apogee Jam+",  # Guitar interface
#   		output_device_name="MacBook Pro Speakers"
# 	) as stream:
# 		# Audio is now streaming through this pedalboard and out of your speakers!		
		

# Program ==============================================================
changeState("hello", "hi :)")
time.sleep(2)
setMenu()

#menu_num = -1
#in_menu = True;
#nextItem()

# next_button.wait_for_press()
# lcd.write_string('You pushed me')


num = 0

# Set the button press functions
next_button.when_pressed = nextItem
select_button.when_pressed = selectItem

while True:
	time.sleep(2)

# Proper GPIO cleanup to release pins after usage
GPIO.cleanup()

