import math        #import needed modules
import pyaudio     #sudo apt-get install python-pyaudio
from cmu_graphics import *
# CODE FROM STACK OVERFLOW https://stackoverflow.com/questions/9770073/sound-generation-synthesis-with-python
# JUST SO I COULD FAMILARIZE MYSELF WITH PYAUDIO

def onAppStart(app):
   pass

PyAudio = pyaudio.PyAudio     #initialize pyaudio
BITRATE = 16000     #number of frames per second/frameset.      

FREQUENCY = 500     #Hz, waves per second, 261.63=C4-note.
LENGTH = 1   #seconds to play sound

BITRATE = max(BITRATE, FREQUENCY+100)

NUMBEROFFRAMES = int(BITRATE * LENGTH)
RESTFRAMES = NUMBEROFFRAMES % BITRATE
WAVEDATA = ''    

#generating wawes
for x in range(NUMBEROFFRAMES):
 WAVEDATA = WAVEDATA+chr(int(math.cos(x/((BITRATE/FREQUENCY)/math.pi))*127+128))

for x in range(RESTFRAMES): 
 WAVEDATA = WAVEDATA+chr(128)

 
p = PyAudio()
stream = p.open(format = p.get_format_from_width(1), 
                channels = 1, 
                rate = BITRATE, 
                output = True)


def onKeyPress(app, key):       #Basic test for controlling pyaudio via cmu_graphics WORKS!!!
    if key == 'p':   
        stream.start_stream()
        stream.write(WAVEDATA)
        stream.stop_stream()
        # stream.close()
       

def main():
    runApp()

main()

