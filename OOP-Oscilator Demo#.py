#Oscilator Demo#
#Used Ideas/code from https://plainenglish.io/blog/making-a-synth-with-python-oscillators-2cb8e68e9c3b, --- published by 'Alan'
#https://github.com/18alantom/synth/blob/main/Code%20Oscillators.ipynb ---- published by 'Alan'
#Specifically the archetecture of oscilator objects 
#In my project though I plan on creating an original 'sequencer' object 

import pyaudio
import math
import itertools

class Oscillator:
    def __init__(self, freq, amp=1, sampleRate=44100,
                 waveRange=(-1,1)):
        pass

def makeSinWave(freq, amp=1, samplerate=44100):            #From Alan
    increment = (2*math.pi * freq) / samplerate
    return ((math.sin(v) * amp) for v in itertools.count(start=0, step=increment))

osc = makeSinWave(freq=440)
samples = [next(osc) for i in range(512)]
print(samples)

class SineOscillator(Oscillator):
    def _post_freq_set(self):
        self.step = (2 * math.pi * self.f) / self.sampleRate
        
    def _post_phase_set(self):
        self._p = (self._p / 360) * 2 * math.pi
        
    def _initialize_osc(self):
        self._i = 0
        
    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if self.waveRange is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


stream = p.open(format = p.get_format_from_width(1), 
                channels = 1, 
                rate = BITRATE, 
                output = True)

