from pedalboard.io import AudioFile, AudioStream
class IOManager:
	def __init__(self):
		self.input_devices = AudioStream.input_device_names
		self.output_devices = AudioStream.output_device_names
		self.input_i = 0
		self.output_i = 0
		
		print("\n" + "-" * 100)
		print("Input Devices:")
		for device in self.input_devices:
			print(device)
			
		print("\nOutput Devices:")
		for device in self.output_devices:
			print(device)
		print("-" * 100 + "\n")
				
		print("Successfully initialized the IOManager")
		
	def __str__(self):
		return f"<IOManager object>"
	
	def refreshIODevices(self, in_or_out):
		match in_or_out:
			case "in":
				input_devices = sd.query_devices(kind = "input")
				input_devices = input_devices.get("name")
				print("Input Devices")
				print(input_devices)
				return input_devices
			case "out":
				output_devices = sd.query_devices(kind = "output")
				output_devices = output_devices.get("name")
				print("Output Devices")
				print(output_devices)
				return output_devices
				
	def getIODevices(self, in_or_out):
		match in_or_out:
			case "in":
				return self.input_devices
			case "out":
				return self.output_devices
	
	def getCurrentIO(self, in_or_out):
		match in_or_out:
			case "in":
				return self.getIOName(in_or_out, self.input_i)
			case "out":
				return self.getIOName(in_or_out, self.output_i)
	
	def getIOName(self, in_or_out, index):
		match in_or_out:
			case "in":
				return self.input_devices[index]
			case "out":
				return self.output_devices[index]
