#MAIN SEQUENCER APP#
from SynthClasses import DrumSynth, Oscillator, ADSR, Sequencer
from threading import *
import pyaudio 
import numpy as np
from cmu_graphics import *
import pedalboard as pb

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
        kick = DrumSynth(
            [
            Oscillator(
                length=kickLength, freq=app.kickFreq, amp=app.kickAmp,
                wave=app.kickWaveType
                )
            ],
            ADSR(
                length=kickLength, attack=app.kickA, 
                decay=app.kickD, sustainLength=app.kickSusLen,
                sustainLevel=app.kickSusLev, release=app.kickR
                ),
            dB=app.kick_dB
            )
        return kick.getSamples()
    def setSnare():
        snareLength = app.lengthOfCell
        app.snareFreq = 380
        app.snarePitchedAmp = .6
        app.snarePitchedWave = 'triangle'
        app.snareNoiseAmp = .4
        app.snareA = .1
        app.snareD = .3
        app.snareSusLen = .2
        app.snareSusLev = 1
        app.snareR = .4
        app.snare_dB = -3
        app.snareFilterCutoff = 500
        app.snareFilterMode = pb.LadderFilter.Mode.HPF24
        app.snareFilterRes = .5
        app.snareFilterDrive = 1
        snare = DrumSynth(
            [
            Oscillator(
                length=snareLength, freq=app.snareFreq,
                amp=app.snarePitchedAmp, wave=app.snarePitchedWave
                ),
            Oscillator(
                length=snareLength, freq=None, amp=app.snareNoiseAmp, wave='whiteNoise'
                )
            ], 
            ADSR(
                length=snareLength, attack=app.snareA, decay=app.snareD, 
                sustainLength=app.snareSusLen, sustainLevel=app.snareSusLev,
                release=app.snareR
                ),
            pb.LadderFilter(
                mode=app.snareFilterMode,
                cutoff_hz=app.snareFilterCutoff,
                resonance=app.snareFilterRes,
                drive=app.snareFilterDrive
                ),
            dB=app.snare_dB
            )
        
        return snare.getSamples()
    def setClHH():
        clHHLength = app.lengthOfCell
        app.clHHAmp = 1
        app.clHHA = .01
        app.clHHD = .1
        app.clHHSusLen = .1
        app.clHHSusLevel = .8
        app.clHHR = .1
        app.clHHFilterFreq = 10000
        app.clHHFilterRes = .8
        app.clHH_dB = -1
        clHH = DrumSynth(
            [
            Oscillator(
                length=clHHLength, freq=None, amp=app.clHHAmp, wave='whiteNoise'
                )
            ],
            ADSR(
                length=clHHLength, attack=app.clHHA,
                decay=app.clHHD, sustainLength=app.clHHSusLen,
                sustainLevel=app.clHHSusLevel,
                release=app.clHHR
                ),
            pb.LadderFilter(
                mode=pb.LadderFilter.Mode.HPF24,
                cutoff_hz=app.clHHFilterFreq,
                resonance=app.clHHFilterRes,
                drive=3
                ),
            dB=app.clHH_dB
            )
        return clHH.getSamples()
    def setOHH():
        oHHLength = app.lengthOfCell
        app.oHHAmp = 1
        app.oHHA = .1
        app.oHHD = .2
        app.oHHSusLen = .4
        app.oHHSusLev = .8
        app.oHHR = .3
        app.oHHFilterFreq = 9000
        app.oHHFilterRes = .4
        app.oHHFilterDrive = 8
        app.oHH_dB = -1
        oHH = DrumSynth(
            [
            Oscillator(
                length=oHHLength, freq=None, amp=app.oHHAmp, wave='whiteNoise'
                )
            ],
            ADSR(
                length=oHHLength, attack=app.oHHA,
                decay=app.oHHD, sustainLength=app.oHHSusLen,
                sustainLevel=app.oHHSusLev, release=app.oHHR
                ),
            pb.LadderFilter(
                mode=pb.LadderFilter.Mode.HPF24, 
                cutoff_hz=app.oHHFilterFreq,
                resonance=app.oHHFilterRes,
                drive=app.oHHFilterDrive
                ),
            dB=app.oHH_dB
            )
        return oHH.getSamples()
    def setLoTom():
        tomLength = app.lengthOfCell
        app.tomWave = 'sawtooth'
        app.loTomPitch = 120
        app.loTomAmp = .8
        app.loTomA = .01
        app.loTomD = .1
        app.loTomSusLen = .2
        app.loTomSusLev = .4
        app.loTomR = .5

        loTom = DrumSynth(
            [
            Oscillator(
                length=tomLength, freq=app.loTomPitch, amp=app.loTomAmp,
                wave=app.tomWave
                )
            ],
            ADSR(
                length=tomLength, attack=app.loTomA, decay=app.loTomD,
                sustainLength=app.loTomSusLen, sustainLevel=app.loTomSusLev,
                release=app.loTomR
                ) 
        )
        return loTom.getSamples()
    def setHiTom():
        tomLength = app.lengthOfCell
        app.hiTomFreq = 420
        app.hiTomAmp = .6
        app.hiTomA = .01
        app.hiTomD = .1
        app.hiTomSusLen = .2
        app.hiTomSusLev = .4
        app.hiTomR = .5
        hiTom = DrumSynth(
            [
            Oscillator(
                length=tomLength, freq=app.hiTomFreq, amp=app.hiTomAmp,
                wave=app.tomWave
            )
            ],
            ADSR(
                length=tomLength, attack=app.hiTomA, decay=app.hiTomD,
                sustainLength=app.hiTomSusLen, sustainLevel=app.hiTomSusLev,
                release=app.hiTomR
                )
        )
        return hiTom.getSamples()
    

    app.samples['kick'] = setKick()
    app.samples['snare'] = setSnare()
    app.samples['clHH'] = setClHH()
    app.samples['oHH'] = setOHH()
    app.samples['loTom'] = setLoTom()
    app.samples['hiTom'] = setHiTom()

    
    
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
            'oHH' : Sequencer(app.sequenceLists[3], app.samples['oHH']),
            'loTom' : Sequencer(app.sequenceLists[4], app.samples['loTom']),
            'hiTom' : Sequencer(app.sequenceLists[5], app.samples['hiTom'])
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

def sequencerScreen_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='slateGray')
    drawLabel('DKTheThinker Proprietary DrumSynth', app.width/2, 20, 
              font='monospace', fill='indigo', bold=True, size=30)
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
    if key == 'space':
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