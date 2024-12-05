import pygame
from Effect import Effect
from pedalboard import Pedalboard, Compressor, Chorus, Delay, Reverb, Gain, load_plugin
from pedalboard.io import AudioFile, AudioStream
from IOManager import IOManager
import time

# from playsound import playsound
class AudioManager:
	def __init__(self, effects_names):
		self.effects_array = [Effect(name) for name in effects_names]
		self.effects_board = Pedalboard([])
		
		self.io_manager = IOManager()
		
		input_device_name = self.io_manager.getCurrentIO("in")
		output_device_name = self.io_manager.getCurrentIO("out")
		# self.stream_obj = AudioStream(input_device_name=output_device_name, output_device_name=output_device_name)
		
		# input_devices
		# output_devices
		# input_devices_i
		# output_devices_i
		# stream_obj
		
		self.audiostream_enabled = False
		
		print("Successfully initialized the AudioManager")
		
		
	def __str__(self):
		return f"<AudioManager object>"
	
	def isEffectParam(self, check_str, effect_index):
		isParam = any(sub_str in check_str for sub_str in self.effects_array[effect_index].getParamNames())
		return isParam
	
	def nextEffectParam(self, effect_index, param_index):
		self.effects_array[effect_index].nextParamValue(param_index)
		
	def getEffectsArray(self):
		return self.effects_array
		
	def enableDisableEffect(self, effect_num, en_dis):
		match en_dis:
			case "enable":
				self.effects_array[effect_num].setEnable(True)
			case "disable":
				self.effects_array[effect_num].setEnable(False)
		
	def isEffect(self, effect_name):
		i = 0
		while i < len(self.effects_array) and self.effects_array[i].getName() != effect_name:
			i = i + 1
		
		if i >= len(self.effects_array):
			return False
		else:
			return True
	
	def getEffectObj(self, effect_name):
		i = 0
		while i < len(self.effects_array) and self.effects_array[i].getName() != effect_name:
			print(self.effects_array[i].getName())
			print(effect_name)
			print(i)
			i = i + 1
		
		return self.effects_array[i]
		
	def updateBoard(self):
		self.effects_board = Pedalboard([
		Gain(gain_db=0),
		])
		
		effect_num = 1
		
		for effect in self.effects_array:
			if effect.getEnable():
				match effect.getName():
					case "Chorus":
						self.effects_board.append(Chorus())
					case "Delay":
						self.effects_board.append(Delay())
					case "Phasor":
						self.effects_board.append(Phasor())
					case "Reverb":
						self.effects_board.append(Reverb())
					case "Compressor":
						self.effects_board.append(Compressor())
				
				for param_i in range(len(effect.getParamNames())):
					param_name = effect.getParamNameAt(param_i)
					param_val = effect.getParamValueAt(param_i)
					self.effects_board[effect_num]
					exec("self.effects_board[effect_num]." + param_name + " = " + str(param_val))
				effect_num = effect_num + 1

	def applyEffects(self, audio_file):
		samplerate = 44100.0
		with AudioFile(audio_file).resampled_to(samplerate) as f:
			audio_in = f.read(f.frames)
		
		audio_out = self.effects_board(audio_in, samplerate)
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
						
	def startAudioStream(self, input_dev, output_dev):
		self.stream_obj = AudioStream(input_dev, output_dev)
		self.stream.plugins = self.effects_board
		self.stream_obj.run()
		
	def stopAudioStream(self):
		stream_obj.close()
	
