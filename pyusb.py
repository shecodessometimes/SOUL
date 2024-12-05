import usb.core
import usb.util
import time
import sounddevice as sd

# Using sounddevice
input_devices = sd.query_devices(kind = "input")
print("Input Devices")
print(input_devices.get("name"))
print(input_devices)

output_devices = sd.query_devices(kind = "output")
print("Output Devices")
print(output_devices.get("name"))
print(output_devices)

hostapi = sd.query_devices()
print("Output Devices")
print(hostapi)

# Iterate through the devices and display formatted info
for i, device in enumerate(hostapi):
    print(f"Index: {i}")
    print(f"   Name: {device['name']}")
    print(f"   Host API: {device['hostapi']}")
    print(f"   Max Input Channels: {device['max_input_channels']}")
    print(f"   Max Output Channels: {device['max_output_channels']}")
    print("-" * 40)

# # Print all USB device ids ---------------------------------------------
# # Find all USB devices
# devices = usb.core.find(find_all=True)

# # Loop through all connected devices
# for device in devices:
# #     print(f"Device: {device}")
    # print(f"Vendor ID: {hex(device.idVendor)}")
    # print(f"Product ID: {hex(device.idProduct)}")
    # print(f"Device Address: {device.address}")
    # # print(f"Device Description: {usb.util.get_string(device, device.iProduct)}")
    # print('-' * 30)
    
# # Find the USB device for audio in -------------------------------------
# vendor_id = 0x1b3f
# product_id = 0x2008
# dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

# # Check if the device was found
# if dev is None:
    # raise ValueError('Device not found')

# # Set the active configuration (this is needed to communicate with the device)
# dev.set_configuration()

# # Endpoint addresses (you may need to find these for your specific device)
# # Typically, 0x81 is the IN endpoint (read), and 0x01 is the OUT endpoint (write)
# endpoint_in = 0x81  # Endpoint address for reading data (usually IN)
# endpoint_out = 0x01  # Endpoint address for writing data (usually OUT)

# # Stream data (reading data from the device)
# try:
    # while True:
        # # Read 64 bytes from the IN endpoint (change the size as needed)
        # data = dev.read(endpoint_in, 64)
        
        # # Process the received data (for example, print it)
        # print("Received Data:", data)
        
        # # Optionally, you can perform some action, like writing data to the device
        # # For example, sending a simple byte to the OUT endpoint
        # # dev.write(endpoint_out, b'\x01')  # Sending byte to OUT endpoint
        
        # # Sleep for a short time to prevent overwhelming the CPU
        # time.sleep(0.1)

# except KeyboardInterrupt:
    # print("Stream interrupted by user.")
