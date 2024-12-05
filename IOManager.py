import sounddevice as sd
class IOManager:
	def __init__(self):
		self.input_i = 0
		self.output_i = 0
		
		#io 
		input_devices = sd.query_devices(kind = "input")
		input_devices = input_devices.get("name")
		output_devices = sd.query_devices(kind = "output")
		output_devices = output_devices.get("name")
		input_devices_i = 0
		output_devices_i = 0
		audiostream_enabled = False
		print(f"input dev: {input_devices} output dev: {output_devices}") 
		in_dev = input_devices[input_devices_i]		
		out_dev = output_devices[output_devices_i]	
		print(f"input dev: {in_dev} output dev: {out_dev}") 
		
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
		match in_out_out:
			case "in":
				return self.input_devices[index].get("name")
			case "out":
				return self.output_devices[index].get("name")
