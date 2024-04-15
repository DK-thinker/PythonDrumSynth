#MAIN SEQUENCER APP#
from SynthClasses import DrumSynth, Oscillator, ADSR, Sequencer
from threading import *
import pyaudio 
import numpy as np
from cmu_graphics import *

sampleRate = 44100
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
        app.waveType = 'sine' #String
        app.kickA = 0.1
        app.kickD = .2
        app.kickSusLength = .3
        app.kickSusLevel = .5
        app.kickR = .2
        kick = DrumSynth([{'length':kickLength, 'freq': app.kickFreq,
                           'amp':app.kickAmp, 'wavetype':app.waveType}],
                        ADSR(length=kickLength, attack=app.kickA, 
                             decay=app.kickD, sustainLength=app.kickSusLength,
                             sustainLevel=app.kickSusLevel, release=app.kickR
                        ))
        return kick.getSamples()
    def setSnare():
        snareLength = 5000
        snare = DrumSynth([
            {'length':snareLength, 'freq':440, 'amp':.1,
            'wavetype':'square'},
            {'length':snareLength, 'freq':20, 'amp':.001,
            'wavetype':'whiteNoise'}
            ], 
            ADSR(length=snareLength, attack=.01, decay=.9, 
                 sustainLength=0, sustainLevel=0, release=.01))
        return snare.getSamples()
    app.samples['kick'] = setKick()
    app.samples['snare'] = setSnare()
    
    
## SEQUENCER SCREEN ##

def sequencerScreen_onScreenActivate(app):
    app.stepi = 0
    app.playing = False
    initializeSequences(app)
    loadSequencerBoard(app)

def initializeSequences(app):
    app.sequences = [[False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16,
                     [False]*16
                     ]
    app.kickSequence = Sequencer(app.sequences[0], app.samples['kick'])
    app.snareSequence = Sequencer(app.sequences[1], app.samples['snare'])

def loadSequencerBoard(app):
    #initializes button objects for the sequencer
    rows, cols = len(app.sequences), len(app.sequences[0])
    buttonW, xSpacing= 40, 10
    buttonH, ySpacing = 80, 10
    OGcx, cy = (app.width//3) + buttonW//2 ,  (app.height//8) + buttonH//2
    for row in range(rows):
        cx = OGcx
        rowOfButtons = []
        for col in range(cols):
            currButton = Button(cx, cy, buttonW, buttonH, onColor='limeGreen',
                                offColor='gainsboro')
            rowOfButtons += [currButton]
            cx += xSpacing + buttonW
        Button.buttons += [rowOfButtons]
        cy += ySpacing + buttonH
    # print(Button.buttons)

def sequencerScreen_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='slateGray')
    drawLabel('DKTheThinker DrumSynth', app.width/2, 20, font='monospace',
              fill='indigo', bold=True, size=30)
    drawSequencer(app)
    drawPlayHead(app)

def drawPlayHead(app):
    pass


def drawSequencer(app):
    for buttonRow in Button.buttons:
        for button in buttonRow:
            button.drawButton()

def sequencerScreen_onMousePress(app, mouseX, mouseY):
    rows, cols = len(Button.buttons), len(Button.buttons[0])
    checkAndHandleSequencerPress(app, mouseX, mouseY, rows, cols)

def checkAndHandleSequencerPress(app, mouseX, mouseY, rows, cols):
    for row in range(rows):
        for col in range(cols):
            #get the pressed row and col of pressed button
            #update the corresponding row and col of app.sequences
            Button.buttons[row][col].checkPressInButton(mouseX, mouseY)
            if Button.buttons[row][col].pressed:
                app.sequences[row][col] = True
            elif not(Button.buttons[row][col].pressed):
                app.sequences[row][col] = False
    prettyPrint(app.sequences)

def sequencerScreen_onKeyPress(app, key):
    if key == 'p':
        if app.playing == True:
            #reset the step index to 0 on every pause
            app.stepi = 0
        app.playing = not (app.playing)


def sequencerScreen_onStep(app):
    if app.playing:
        app.stepi %= 16
        #make this more general by sequence in app.sequences[sequence].handel:
        app.kickSequence.handleStep(app.stepi)
        app.snareSequence.handleStep(app.stepi)
        print(app.stepi)
        app.stepi += 1

def prettyPrint(L):
    print()
    for row in L:
        print(row)

## SOUND EDITOR SCREENS ##




## GUI CLASSES ##

class Button:

    buttons = []

    def __init__(self, cx, cy, width, height, onColor='limeGreen', 
                 offColor='gainsboro'):
        self.leftX = cx - width//2
        self.topY = cy - height//2
        self.width = width
        self.height = height
        self.onColor = onColor
        self.offColor = offColor
        self.pressed = False

    def __repr__(self):
        return f'Button({self.leftX},{self.topY}), pressed:{self.pressed}'

    def drawButton(self):
        if self.pressed:
            color = self.onColor
        elif self.pressed == False:
            color = self.offColor
        # color = self.onColor if self.pressed else self.offColor
        drawRect(self.leftX, self.topY, self.width, self.height,
                 fill=color, border='black')

    def checkPressInButton(self, mouseX, mouseY):
        if (self.leftX <= mouseX <= self.leftX + self.width and
            self.topY <= mouseY <= self.topY + self.height):
            self.pressed = not(self.pressed)
        
def main():
    runAppWithScreens(initialScreen='sequencerScreen')

main()