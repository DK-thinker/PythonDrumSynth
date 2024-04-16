#MAIN SEQUENCER APP#
from SynthClasses import DrumSynth, Oscillator, ADSR, Sequencer
from threading import *
import pyaudio 
import numpy as np
from cmu_graphics import *

sampleRate = 44100.0
pa = pyaudio.PyAudio()

'''
@TODO 
Build rest of the sounds
figure out volume
add knobs and macrocontrols
add moving playhead

'''

def onAppStart(app):
    app.width = 1280
    app.height = 720
    app.bpm = Sequencer.bpm 
    setOnStepFromBPM(app)
    initializeSamples(app)

def setOnStepFromBPM(app):
    secondsPerBeat = 60/app.bpm
    app.lengthOfCell = (secondsPerBeat / 16) * sampleRate
    app.stepsPerSecond = 4 / secondsPerBeat #4 1/16 notes per beat

def initializeSamples(app):
    app.samples ={}
    def setKick():
        kickLength = app.lengthOfCell
        app.kickFreq = 60
        app.kickAmp = 1   #int <= 1
        app.kickWaveType = 'sine' #String
        app.kickA = 0.1
        app.kickD = .2
        app.kickSusLen = .3
        app.kickSusLev = .5
        app.kickR = .2
        app.kick_dB = 0
        kick = DrumSynth([{'length':kickLength, 'freq': app.kickFreq,
                           'amp':app.kickAmp, 'wavetype':app.kickWaveType}],
                        ADSR(length=kickLength, attack=app.kickA, 
                             decay=app.kickD, sustainLength=app.kickSusLen,
                             sustainLevel=app.kickSusLev, release=app.kickR),
                        dB=app.kick_dB)
        return kick.getSamples()
    def setSnare():
        snareLength = app.lengthOfCell
        app.snarePitchedFreq = 666
        app.snarePitchedAmp = .7
        app.snarePitchedWave = 'square'
        app.snareNoiseAmp = .3
        app.snareA = .1
        app.snareD = .3
        app.snareSusLen = .4
        app.snareSusLev = 1
        app.snareR = .01
        app.snare_dB = -3
        app.snareFilter = 900.0
        snare = DrumSynth([
            {'length':snareLength, 'freq':app.snarePitchedFreq, 
             'amp':app.snarePitchedAmp,
            'wavetype':app.snarePitchedWave},
            {'length':snareLength, 'freq':None, 'amp':app.snareNoiseAmp,
            'wavetype':'whiteNoise'}
            ], 
            ADSR(length=snareLength, attack=app.snareA, decay=app.snareD, 
                 sustainLength=app.snareSusLen, sustainLevel=app.snareSusLev,
                 release=app.snareR),
            filter=app.snareFilter,
            dB=app.snare_dB)
        return snare.getSamples()
    def setClHH():
        clHHLength = app.lengthOfCell
        app.clHHWavetype = 'whiteNoise'
        app.clHHAmp = 1
        app.clHHA = .01
        app.clHHD = .1
        app.clHHSusLen = .1
        app.clHHSusLevel = .8
        app.clHHR = .1
        app.clHHFilter = 14000
        app.clHH_dB = -1
        clHH = DrumSynth([{'length':clHHLength, 'freq':None, 'amp':app.clHHAmp,
                           'wavetype':app.clHHWavetype}],
                           ADSR(length=clHHLength, attack=app.clHHA,
                                decay=app.clHHD, sustainLength=app.clHHSusLen,
                                sustainLevel=app.clHHSusLevel,
                                release=app.clHHR),
                            filter=app.clHHFilter,
                            dB=app.clHH_dB)
        return clHH.getSamples()
    def setOHH():
        oHHLength = app.lengthOfCell
        app.oHHWavetype = 'whiteNoise'
        app.oHHAmp = 1
        app.oHHA = .2
        app.oHHD = .01
        app.oHHSusLen = .7
        app.oHHSusLev = .9
        app.oHHR = .01
        app.oHHFilter = 16000
        app.oHH_dB = -1
        oHH = DrumSynth([{'length':oHHLength,'freq':None, 'amp':app.oHHAmp,
                          'wavetype':app.oHHWavetype}],
                          ADSR(length=oHHLength, attack=app.oHHA,
                               decay=app.oHHD, sustainLength=app.oHHSusLen,
                               sustainLevel=app.oHHSusLev, release=app.oHHR),
                            filter=app.oHHFilter,
                            dB=app.oHH_dB)
        return oHH.getSamples()

    app.samples['kick'] = setKick()
    app.samples['snare'] = setSnare()
    app.samples['clHH'] = setClHH()
    app.samples['oHH'] = setOHH()
    
    
## SEQUENCER SCREEN ##

def sequencerScreen_onScreenActivate(app):
    app.stepi = 0
    app.playing = False
    initializeSequences(app)
    loadSequencerBoard(app)

def initializeSequences(app):
    app.sequenceLists = [[False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16
                     ]
    app.sequencer = {
            'kick' : Sequencer(app.sequenceLists[0], app.samples['kick']),
            'snare' : Sequencer(app.sequenceLists[1], app.samples['snare']),
            'clHH' : Sequencer(app.sequenceLists[2], app.samples['clHH']),
            'oHH' : Sequencer(app.sequenceLists[3], sample=app.samples['oHH'])
                    }   
def loadSequencerBoard(app):
    #initializes button objects for the sequencer
    rows, cols = len(app.sequenceLists), len(app.sequenceLists[0])
    buttonW, xSpacing= 40, 5
    buttonH, ySpacing = 80, 10
    OGcx, cy = (app.width//3) + buttonW//2 ,  (app.height//8) + buttonH//2
    for row in range(rows):
        cx = OGcx
        rowOfButtons = []
        for col in range(cols):
            currButton = Button(cx, cy, buttonW, buttonH, onColor='limeGreen',
                                offColor='gainsboro')
            rowOfButtons += [currButton]
            #group cells in groups of 4
            if (col+1) % 4 == 0:
                cx += xSpacing*2
            cx += xSpacing + buttonW
        Button.buttons += [rowOfButtons]
        cy += ySpacing + buttonH
    # print(Button.buttons)

def sequencerScreen_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='slateGray')
    drawLabel('DKTheThinker DrumSynth', app.width/2, 20, font='monospace',
              fill='indigo', bold=True, size=30)
    drawSequencer(app)

def drawSequencer(app):
    for buttonRow in Button.buttons:
        for buttonCol in range(len(buttonRow)):
            if buttonCol == app.stepi and app.playing:
                borderColor = 'red'
            else: borderColor = 'black'
            buttonRow[buttonCol].drawButton(borderFill=borderColor)

def sequencerScreen_onMousePress(app, mouseX, mouseY):
    rows, cols = len(Button.buttons), len(Button.buttons[0])
    checkAndHandleSequencerPress(app, mouseX, mouseY, rows, cols)

def checkAndHandleSequencerPress(app, mouseX, mouseY, rows, cols):
    for row in range(rows):
        for col in range(cols):
            #get the pressed row and col of pressed button
            #update the corresponding row and col of app.sequenceLists
            Button.buttons[row][col].checkPressInButton(mouseX, mouseY)
            app.sequenceLists[row][col] = Button.buttons[row][col].pressed

def sequencerScreen_onKeyPress(app, key):
    if key == 'p':
        if app.playing == True:
            #reset the step index to 0 on every pause
            app.stepi = 0
        app.playing = not (app.playing)


def sequencerScreen_onStep(app):
    if app.playing:
        for sequence in app.sequencer:
            app.sequencer[sequence].handleStep(app.stepi)
        app.stepi = (app.stepi+1) % 16

def prettyPrint(L):
    print()
    for row in L:
        print(row)

## SOUND EDITOR SCREENS ##




## GUI CLASSES ##

class Button:

    buttons = []

    def __init__(self, cx, cy, width, height, onColor='limeGreen', 
                 offColor='red'):
        self.leftX = cx - width//2
        self.topY = cy - height//2
        self.width = width
        self.height = height
        self.onColor = onColor
        self.offColor = offColor
        self.pressed = False

    def __repr__(self):
        return f'Button({self.leftX},{self.topY}), pressed:{self.pressed}'

    def drawButton(self, borderFill=None):
        if self.pressed:
            color = self.onColor
        elif not(self.pressed):
            color = self.offColor
        # color = self.onColor if self.pressed else self.offColor
        drawRect(self.leftX, self.topY, self.width, self.height,
                 fill=color, border=borderFill, borderWidth=2)

    def checkPressInButton(self, mouseX, mouseY):
        if (self.leftX <= mouseX <= self.leftX + self.width and
            self.topY <= mouseY <= self.topY + self.height):
            self.pressed = not(self.pressed)

        
def main():
    runAppWithScreens(initialScreen='sequencerScreen')

main()