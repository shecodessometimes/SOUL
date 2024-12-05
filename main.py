import time
from gpiozero import Button

from AudioManager import AudioManager
from LCDManager import LCDManager
from IOManager import IOManager
from Effect import Effect

# Initialize ===========================================================
next_button_pin = 3
select_button_pin = 2
rs_pin = 37
enable_pin = 35
data_4_pin = 33
data_5_pin = 31
data_6_pin = 29
data_7_pin = 23

effects_list = ["Chorus", "Delay", "Reverb", "Compressor"]

# Manager objects
audio_manager = AudioManager(effects_list)
lcd_manager = LCDManager(next_button_pin, select_button_pin, rs_pin, enable_pin, 
				data_4_pin, data_5_pin, data_6_pin, data_7_pin)
io_manager = IOManager()
state_manager = StateManager(audio_manager, lcd_manager, io_manager)

# Buttons
next_button = Button(3); # next-button connected to GPIO2
select_button = Button(2); # select-button connected to GPIO3
button_pressing = 0

# Functions ============================================================
def nextItem():
	global button_pressing
	button_pressing = button_pressing + 1
	if button_pressing == 1:
		state_manager.nextItemState()
		button_pressing = 0
			
def selectItem():
	global button_pressing
	button_pressing = button_pressing + 1
	if button_pressing == 1:
		state_manager.selectItemState()
		time.sleep(1)
		button_pressing = 0

# Program ==============================================================
state_manager.changeState("hello", "hi :)")
time.sleep(2)
state_manager.changeState("menu", "")

# Set the button press functions
next_button.when_pressed = nextItem
select_button.when_pressed = selectItem

while True:
	time.sleep(2)

# Proper GPIO cleanup to release pins after usage
lcd_manager.cleanGPIO()


