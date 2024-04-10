### Oscillator 2.0 ###


''' Overall Design:
Create int arrays of each sample wav and add to dictionary.
On each step of the sequencer, check what samples are on and sum them
then write the summed data to the speaker.


Envelope Design:
given the wave data array, create an amplitude array and multiply the two.
the post-envelope array will be the one added to the sample dict.

## CITATIONS ##
Used Ideas from https://plainenglish.io/blog/making-a-synth-with-python-oscillators-2cb8e68e9c3b, 
    #https://github.com/18alantom/synth/blob/main/Code%20Oscillators.ipynb 
    Both of the above are from the same guy, 'Alan'

Referecend https://antreith.wordpress.com/2018/05/12/elementary-signal-generation-with-python/ 
    and https://www.brownnoiseradio.com/resources/generating-white-noise-in-python%3A-a-step-by-step-guide
    For wave and white noise generation



'''

from cmu_graphics import *
import numpy as np
import pyaudio 
import itertools
from scipy import signal as sg
import math
import matplotlib.pyplot as plt

#### BIG TOP DOWN DESIGN ####
'''
@TODO look at threading and see where it can be applied

Create windows for sample manipulation, sequencing/mixing(vol knob).

Each window must update appropriate values 

    Sample Manipulation Window:

        Should update values of the DrumSynth sub-class, generate the wave 
        and add the finalized sample to app.sampleDictionary

    Sequencer Window:

        -Button of drum type must open the corresponding sample manipulation
        window. (Must make a button type for this)
        -Sequencer (buttons again) modifies app.sequences or whatever
        -Play/pause button
            This will cause the audio to be compiled into buffers, 
            ideally you can have samples longer than a cell, so you must
            implement a buffer
         * Tangental ideas for the buffer:
            Key is for the sequence to be editable as it is playing, 
            so generating a byte array with length of all 16 steps
            won't work
        -volume knob



'''


pa = pyaudio.PyAudio()
sampleRate = 44100

stream = pa.open(output=True,
                channels=1,
                rate=44100,
                format=pyaudio.paInt16,
                frames_per_buffer=256,
                )
    
def  getLengthOfOneCell(app):
    #16 cells in total,
    secondsOfBeat = (60/app.bpm) #gets seconds per beat
    samplesOfBeat = secondsOfBeat * sampleRate
    app.cellLength = 44100
   
def onAppStart(app):
    app.bpm = 60
    getLengthOfOneCell(app)
    app.samples = {}    #dict of {sampleName : 16bit array}. will update whenever a sound is changed
    
class Oscillator:

# maybe switch app.cellLength for a length, which can allow for longer sample generation.
# Sample lengths longer than the app.cellLength can be introduced with a buffer
# cueing proccess later on.

    def __init__(self, paramaters):   #Paramaters is {length, freq, amp, wavetype}
        self.length = paramaters['length'] #In samples
        self.freq = paramaters['freq']
        self.amp = paramaters['amp']
        self.wave = paramaters['wavetype']
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

    def __init__(self, oscParamaters, envelope):
        self.oscParamaters = oscParamaters  # List of dictionaries of args to send to the oscillator
        self.envelope = envelope  

    def getWavesFromOscillator(self):
        waves = []
        for paramaters in self.oscParamaters:
            signal = Oscillator(paramaters)
            waveArray = signal.generateWaveArray()
            waves.append(waveArray)
        return waves
        
    def waveAdder(self):
        waves = self.getWavesFromOscillator()
        return sum(waves)
        
    def ampModulation(self):
        wave = self.waveAdder()
        print('wave',wave)
        env = ADSREnvelope.generateEnvArray(self.envelope)
        return np.multiply(wave, env)
    
    def getSamples(self):            #From Alan / Maybe move this out of the class
        wave = self.ampModulation()
        print('ModWave', wave)
        x = np.arange(len(wave))
        y = wave
        plt.xlabel('sample(n)')
        plt.ylabel('voltage(V)')
        plt.show()
        # print(wave)
        return [int((wave[i]) * 32767) for i in range(len(wave))]
    

class ADSREnvelope:

    # Must pass in attack and decay values such that (a+d+s+r) <= 1
    def __init__(self, length, attack, decay, sustainLength, sustainLevel, release):
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
        return (-(self.sustainLevel * x) / self.rLengthInSamples) + self.sLengthInSamples

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
 
        # x = np.arange(app.cellLength)
        # y = envArray
        # plt.plot(x, y)
        # plt.xlabel('time')
        # plt.ylabel('amp')
        # plt.show()
        # print(envArray)
        return envArray
        

def onKeyPress(app, key):
    if key == 'p':
        kickParamaters = [{'length':22050, 'freq':80, 'amp':1, 'wavetype':'sawtooth'},
                          {'length':22050, 'freq':60, 'amp':1, 'wavetype':'sine'}]
        kickEnvelope = ADSREnvelope(length=22050, attack=.01, decay=.3,
                                     sustainLength=.3, sustainLevel=.2, release=.3)        
        kick = DrumSynth(kickParamaters, kickEnvelope)
        kickSample = kick.getSamples()
        kick = np.int16(kickSample).tobytes()
        stream.write(kick)
        # stream.close()

def main():
    runApp()
    # openAudioStream()
    # print(pa.get_host_api_info_by_index())
    

main()