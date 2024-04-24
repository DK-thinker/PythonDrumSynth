### Oscillator 2.0 ###

## CITATIONS ##

import numpy as np
import pyaudio 
from threading import Thread
from scipy import signal as sg
import math
import matplotlib.pyplot as plt

#### BIG TOP DOWN DESIGN ####

pa = pyaudio.PyAudio()
sampleRate = 44100.0
    
class Oscillator:

    def __init__(self, length, freq, amp, wave):  
        self.length = length #In samples
        self.freq = freq    #int
        self.amp = amp  #int <= 1
        self.wave = wave    #String
        if self.wave not in {'sine', 'triangle', 'sawtooth', 'square',
                             'whiteNoise'}:
            raise Exception('Spell your waveType correctly')
        if self.freq != None:
            self.period = (2 * math.pi * self.freq) / sampleRate

    def sineGenerator(self, x):
        return (math.sin(self.period*x)) * self.amp
    
    def triangleGenerator(self, x):
        return self.amp * sg.sawtooth(self.period*x, width=.5)
    
    def squareGenerator(self, x):
        return self.amp * sg.square(self.period*x)
    
    def sawtoothGenerator(self, x):
        return self.amp * sg.sawtooth(self.period*x)
    
    def generateWaveArray(self):
        oscArray = np.empty(int(self.length))

        if self.wave == 'whiteNoise':
                oscArray = np.random.normal(0, 1, len(oscArray))
                oscArray *= self.amp
        else:
            for x in range(len(oscArray)):
                if self.wave == 'sine':
                    oscArray[x] = self.sineGenerator(x)

                elif self.wave == 'triangle':
                    oscArray[x] = self.triangleGenerator(x)

                elif self.wave == 'square':
                    oscArray[x] = self.squareGenerator(x)
            
                elif self.wave == 'sawtooth':
                    oscArray[x] = self.sawtoothGenerator(x)
        return oscArray
    
class DrumSynth:
    sampleNum = 0

    def __init__(self, oscillators, envelope, filter=None, vol=1):
        self.oscillators = oscillators # List of oscillator objects
        self.envelope = envelope  
        self.vol = vol
        self.filter = filter
        DrumSynth.sampleNum += 1

    def __repr__(self):
        return f'sample {DrumSynth.sampleNum}'

    def getWavesFromOscillator(self):
        waves = []
        for wave in self.oscillators:
            waveArray = wave.generateWaveArray()
            waves.append(waveArray)
        return waves
    
    def filterWave(self, wave):
        return self.filter.process(input_array=wave, sample_rate=sampleRate)

    def waveAdder(self):
        waves = self.getWavesFromOscillator()
        return sum(waves)
        
    def ampModulation(self):
        wave = self.waveAdder()
        env = self.envelope.generateEnvArray()
        modedWave = self.makeSureWavesDontClip(np.multiply(wave, env))
        return np.multiply(wave, env)
    
    def makeSureWavesDontClip(self, wave):  # This func is loosely From Alan
        #squish values to be between -1 and 1
        peak = np.max(wave)
        if peak > 1:
            amountToShrink = 1 / peak
            return (wave * amountToShrink) * self.vol
        else:
            return wave * self.vol
    
    def getSamples(self):            #From Alan
        wave = self.ampModulation()
        wave *= self.vol
        sample = np.float32(wave)
        if self.filter != None:
            sample = self.filterWave(sample)
        return sample.tobytes()

class ADSR:

    # Must pass in attack and decay values such that (a+d+s+r) <= 1
    def __init__(self, length, attack, decay, sustainLength, sustainLevel, release):
        if attack+decay+sustainLength+release > 1:
            raise Exception('ADSR lengths must sum to <= 1')
        self.envelopeLength = length
        self.aLengthInSamples = math.floor(self.envelopeLength * attack)
        self.dLengthInSamples = math.floor(self.envelopeLength * decay)
        self.sLengthInSamples = math.floor(self.envelopeLength * sustainLength)
        self.rLengthInSamples = math.floor(self.envelopeLength * release)
        self.sustainLevel = sustainLevel
    
    def generateAttackVals(self, x):
        return (x/self.aLengthInSamples)
    
    def generateDecayVals(self, x):
        return ((1* x) /self.dLengthInSamples) + 1
    
    def generateReleaseVals(self, x):
        return (-(self.sustainLevel * x) / self.rLengthInSamples
                 + self.sLengthInSamples)

    def generateEnvArray(self):
        
        attackEnd = self.aLengthInSamples
        decayEnd = attackEnd + self.dLengthInSamples
        sustainEnd = decayEnd + self.sLengthInSamples
        releaseEnd = sustainEnd + self.rLengthInSamples
        envArray = np.zeros(int(self.envelopeLength))

        for x in range(1, len(envArray)):
            ampVal = 0
            if x < attackEnd:
                ampVal = x/self.aLengthInSamples
            elif attackEnd <= x < decayEnd:
                slope = (self.sustainLevel - 1) / self.dLengthInSamples
                ampVal = (x - attackEnd) * slope + 1
            elif decayEnd <= x < sustainEnd:
                ampVal = self.sustainLevel
            elif sustainEnd <= x < releaseEnd:
                slope = (-self.sustainLevel) / self.rLengthInSamples
                ampVal = (x - sustainEnd) * slope + self.sustainLevel
            envArray[x] = ampVal
        return envArray
    
class Sequencer:
    bpm = 130
    totalCreated = 0

    def initSeqStream(self):
        self.stream = pa.open(output=True,
                    channels=1,
                    rate=int(sampleRate),
                    format=pyaudio.paFloat32,
                    frames_per_buffer=256,
                    )

    def __init__(self, sequence, sample):
        self.initSeqStream()
        self.sequence = sequence
        self.sample = sample
        Sequencer.totalCreated += 1

        #32 bit byte array is 2x the length of samples
        self.sampleLength = len(sample) // 2 

        self.playing = False
        self.openThread()
        
    def openThread(self):
        self.thread = Thread(target=self.writeToStream, args=(False,),
                              daemon=True)
        self.thread.start()
        
    def handleStep(self, i):
        if self.sequence[i] == 1:
            if self.stream.is_stopped():
                self.stream.start_stream()
            self.writeToStream()
    
    def writeToStream(self, actuallyWrite=True):
            # actuallyWrite fixes bug with samples playing on thread 
            # initiazition
            if actuallyWrite:
                self.stream.write(self.sample)
