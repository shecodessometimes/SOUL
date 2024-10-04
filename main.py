import time
from gpiozero import Button
from RPLCD.gpio import CharLCD  # Ensure you're using the GPIO version of CharLCD
import RPi.GPIO as GPIO
from Effect import Effect

# Initialize ===========================================================
next_button = Button(2); # next-button connected to GPIO2
select_button = Button(3); # select-button connected to GPIO3

# Set GPIO numbering mode to BOARD or BCM
GPIO.setmode(GPIO.BOARD)  # Use GPIO.BCM if you are using BCM numbering

# Initialize the LCD (using 4-bit mode) and specify the numbering_mode
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
lcd.cursor_mode = 'blink'

# creating list
menu_array = []
  
# using list comprehension to append instances to list
menu_array += [Effect(name) for name in ["Chord", "Crunch", "Delay", "Reverb", "Slowed", "Loop"]]
  
## if menu_array has an odd number of items, hahaha, it doesn't :)
#if len(menu_array) % 2 == 1:
#	menu_array.append("")

# Functions ============================================================
def helloWorld():
	# Write "Hello world!" to the second row, fourth column
	lcd.cursor_pos = (0,0)  # Row 1 (second row), column 3 (fourth character position)
	lcd.write_string(u'Welcome to SOUL!')
	lcd.cursor_pos = (1,0)  # Row 1 (second row), column 3 (fourth character position)
	lcd.write_string(u'hi :)')
	
def nextItem():
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
		
	# Update LCD
	if menu_num % 2 == 0:
		# Update with menu_array
		lcd.clear()
		for i in range(2):
			lcd.cursor_pos = (i,0)
			effect = menu_array[menu_num + i]
			menu_line = effect.getName() + ' '*(15 - len(effect.getName())) + 'Y'
			print(menu_line)
			lcd.write_string(menu_line)
		
		lcd.cursor_pos = (0,0)
	else:
		lcd.cursor_pos = (1,0)
		
def selectItem():
	lcd.clear()
	
	global in_menu
	global menu_num
	selected = menu_array[menu_num]
	in_menu = False
	lcd.write_string('Selected ' + selected)

# Program ==============================================================
helloWorld()
time.sleep(2)
menu_num = -1
in_menu = True;
nextItem()

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

