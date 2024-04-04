#Oscilator Demo#
#Used Ideas/code from https://plainenglish.io/blog/making-a-synth-with-python-oscillators-2cb8e68e9c3b, --- published by 'Alan'
#https://github.com/18alantom/synth/blob/main/Code%20Oscillators.ipynb ---- published by 'Alan'
# Specifically I read through and learned his approach to an OOP-based oscilator, 
# but I tried to build my Oscilator without directly copying him, 
# but there was inspiration. And any backend type of audio code I took from him
# will be directly stated 

import numpy as np
from cmu_graphics import *
import pyaudio
import math
import itertools

p = pyaudio.PyAudio()


stream = p.open(output=True,
                channels=1,
                rate=44100,
                format=pyaudio.paInt16,
                frames_per_buffer=256
                )
# print(type(stream))

class Oscillator:

    def __init__(self, freq, amp=1, sampleRate=44100):
        self.freq = freq
        self.amp = amp
        self.sampleRate = sampleRate
        self.stepRate = (2*math.pi * self.freq) / self.sampleRate
    


class sinOscillator(Oscillator):

    def __init__(self, freq, amp=1, sampleRate=44100):
        super().__init__(freq)
        self.position = 0

    def generateWave(self):             #From Alan
        increment = (2 * math.pi * self.freq)/ self.sampleRate
        return (math.sin(v) * self.amp for v in itertools.count(start=0, step=increment))
    
    def getSamples(self):               #From Alan
        wave = self.generateWave()
        return [int(next(wave) * 32767) for i in range(256*44100)]



def onAppStart(app):
    app.playing = False


def onKeyPress(app, key):
    if key == 'p':
        print(app.playing)
        if not (app.playing):
            app.playing = True
            # print('playing')
            # stream.start_stream()
            note = sinOscillator(freq=80, amp=1)
            data = np.int16(note.getSamples()).tobytes()
            print(data)
            stream.write(data)
        elif app.playing:
            app.playing = False
            # stream.close()
        
        # print(note.getSamples())


def main():
    # openStream()
    # print('HERE', p.get_default_output_device_info())
    runApp()

main()