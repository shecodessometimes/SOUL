import time
from gpiozero import Button
from RPLCD.gpio import CharLCD  # Ensure you're using the GPIO version of CharLCD
import RPi.GPIO as GPIO
from pedalboard import Pedalboard, Reverb, load_plugin
from pedalboard.io import AudioFile
from Effect import Effect

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

# Create lists
# To definitely do: delay, looping, reverb
# menu_array += [Effect(name) for name in ["Chord", "Crunch", "Delay", "Reverb", "Slowed", "Loop"]]
effects_array = [Effect(name) for name in ["Chorus", "Delay", "Phasor"]]

menu_array = [effect.getName() for effect in effects_array]
menu_array.append("Try sine wave")


modify_array = []

modify_num = 0
  
## if menu_array has an odd number of items, hahaha, it doesn't :)
#if len(menu_array) % 2 == 1:
#	menu_array.append("")

# Functions ============================================================
def nextItem():
	time.sleep(0.5)
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
			
			
def selectItem():
	time.sleep(0.5)
	global current_state
	match current_state:
		case "menu":
			global in_menu
			global menu_num
			effect = menu_array[menu_num]
			if isEffect(effect):
				changeState("modify", effect) # Change the state
			else:
				print("In else! Yay!")
				#play effect
		case "modify":
			global modify_array
			if modify_array[modify_num] == "Enabled":
				effects_array[menu_num].setEnable(False)
				modify_array[modify_num] = "Disabled"
				setLCDLine(modify_array, modify_num)
			elif modify_array[modify_num] == "Disabled":
				effects_array[menu_num].setEnable(True)
				modify_array[modify_num] = "Enabled"
				setLCDLine(modify_array, modify_num)
			elif modify_array[modify_num].lower() == "quit" or modify_array[modify_num].lower() == "back":
				print("back")
				changeState("menu", "quit")
			
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
		print(lines_array)
		print(line_num)
		print(i)
		effect = lines_array[top_line + i]
		if isEffect(effect):
			effect_obj = getEffectObj(effect)
			if effect_obj.getEnable():
				line = effect + ' '*(15 - len(effect)) + 'Y'
			else:
				line = effect + ' '*(15 - len(effect)) + 'N'
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
		modify_array.append("Enabled")
	else:
		modify_array.append("Disabled")
	modify_array.append("back")
	modify_array.append("")
	
	print("modify array:")
	print(modify_array)
	
	# Update LCD
	setLCDLine(modify_array, 0)

def isEffect(effect_name):
	i = 0
	while i < len(effects_array) and effects_array[i].getName() != effect_name:
		print(effects_array[i].getName())
		print(effect_name)
		print(i)
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
	
	#if i >= len(effects_array):
	#	return null
	
	return effects_array[i]

def applyEffects(audioFile):
	with AudioStream(
  		input_device_name="Apogee Jam+",  # Guitar interface
  		output_device_name="MacBook Pro Speakers"
	) as stream:
		# Audio is now streaming through this pedalboard and out of your speakers!
		stream.plugins = Pedalboard([
		Compressor(threshold_db=-50, ratio=25),
		])
		
		for effect in menu_array:
			if effect.getEnabled():
				match effect.getName():
					case "Chorus":
						board.append(Chorus(gain_db=effect.getGain()))
					case "Delay":
						board.append(Delay(gain_db=effect.getGain()))
					case "Phasor":
						board.append(Phasor(gain_db=effect.getGain()))
					case "Reverb":
						board.append(Reverb(gain_db=effect.getGain()))
				
		

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

