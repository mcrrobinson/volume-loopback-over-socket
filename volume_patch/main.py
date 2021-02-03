import pyaudio
import sys
import numpy as np
import zmq

import asyncio
from time import sleep
import aiozmq

defaultframes = 512
device_info = {}

#Use module
p = pyaudio.PyAudio()

device_found = False
# Search for a device that is both default and has WASAPI
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if(p.get_device_info_by_index(i)["name"] == p.get_default_output_device_info()["name"] and (p.get_host_api_info_by_index(info["hostApi"])["name"]).find("WASAPI") != -1):

        print("################################################## \n")
        print (str(info["index"]) + " : " + info["name"] + " - " + p.get_host_api_info_by_index(info["hostApi"])["name"] + "\n")
        print("##################################################")
        device_info = p.get_device_info_by_index(info["index"])
        device_found = True

# TODO Get the individual to pick which non default device to use. 
if(device_found == False):
    if((p.get_host_api_info_by_index(info["hostApi"])["name"]).find("WASAPI") != -1):
        print("##################################################")
        print("This device is supported but is not your default")
        print("device.")
        print(str(info["index"]) + " : " + info["name"] + " - " + p.get_host_api_info_by_index(info["hostApi"])["name"])
        print("In order to get this to work you will need to")
        print("change this to become your output device.")
        print("##################################################")
        device_info = p.get_device_info_by_index(info["index"])
        device_found = True

# If no device is found that is WASAPI capable the code will exit.
if(device_found == False):
    print("There were no devices detected that can be used, do you have WASAPI installed?")
    sys.exit()

# Open stream
channelcount = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
stream = p.open(
    format = pyaudio.paInt16,
    channels = channelcount,
    rate = int(device_info["defaultSampleRate"]),
    input = True,
    frames_per_buffer = defaultframes,
    input_device_index = device_info["index"],
    as_loopback = True
)

async def do():
    rpc_stream = await aiozmq.stream.create_zmq_stream(
        zmq_type=zmq.PUB,
        bind='tcp://192.168.1.222:5556',
    )

    while True:
        data = np.frombuffer(stream.read(2048),dtype=np.int16)
        peak=np.average(np.abs(data))*10
        output=int(round(50*peak/2**16))
        
        # Use Chr isn't the best. Best is to make a struct in the future.
        msg = [chr(output).encode()]
        print(msg[0])
        rpc_stream.write(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(do())

# Stops the recording.
stream.stop_stream()
stream.close()

#Close module
p.terminate()