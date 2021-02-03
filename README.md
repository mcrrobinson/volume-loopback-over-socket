# random-volume-c--scripts

## Pitch Patch
Includes a python patch that records both the audio volume as well as the pitch
using pyaudio (unmodified) & aubio.

## Volume Patch
Includes a python patch that records the volume using a modified versino of
pyaudio that loops back the audio device in the computer to get the speaker
volume. It then sends that information over a socket using ZMQ and Asyncio to
the listener.