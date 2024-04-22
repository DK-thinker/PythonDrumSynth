#MAIN SEQUENCER APP#
from SynthClasses import DrumSynth, Oscillator, ADSR, Sequencer
from guiClasses import Button, Fader
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
    setOnStepFromBPM(app)
    initializeSamples(app)

def setOnStepFromBPM(app):
    secondsPerBeat = 60/Sequencer.bpm
    app.lengthOfCell = (secondsPerBeat / 16) * sampleRate
    app.stepsPerSecond = 4 / secondsPerBeat #4 1/16 notes per beat

def initializeSamples(app):
    app.samples = {} 

    app.kickFreq = 100
    app.kickAmp = 1    #int <= 1
    app.kickWaveType = 'sine' #String
    app.kickA = 0.01
    app.kickD = .4
    app.kickSusLen = .1
    app.kickSusLev = .4
    app.kickR = .1
    app.kick_dB = 0

    app.snareFreq = 200
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

    app.clHHAmp = 1
    app.clHHA = .01
    app.clHHD = .1
    app.clHHSusLen = .1
    app.clHHSusLevel = .8
    app.clHHR = .1
    app.clHHFilterFreq = 10000
    app.clHHFilterRes = .8
    app.clHH_dB = -1

    app.oHHAmp = 1
    app.oHHA = .1
    app.oHHD = .2
    app.oHHSusLen = .4
    app.oHHSusLev = .8
    app.oHHR = .3
    app.oHHFilterFreq = 7000
    app.oHHFilterRes = .9
    app.oHHFilterDrive = 8
    app.oHH_dB = -1

    app.tomWave = 'square'
    app.loTomPitch = 120
    app.loTomAmp = .8
    app.loTomA = .01
    app.loTomD = .1
    app.loTomSusLen = .2
    app.loTomSusLev = .4
    app.loTomR = .5

    app.hiTomFreq = 420
    app.hiTomAmp = .6
    app.hiTomA = .01
    app.hiTomD = .1
    app.hiTomSusLen = .2
    app.hiTomSusLev = .4
    app.hiTomR = .5

    app.samples['kick'] = setKick(app).getSamples()
    app.samples['snare'] = setSnare(app).getSamples()
    app.samples['clHH'] = setClHH(app).getSamples()
    app.samples['oHH'] = setOHH(app).getSamples()
    app.samples['loTom'] = setLoTom(app).getSamples()
    app.samples['hiTom'] = setHiTom(app).getSamples()

def setKick(app):
    kick = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=app.kickFreq, amp=app.kickAmp,
            wave=app.kickWaveType
            )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.kickA, 
            decay=app.kickD, sustainLength=app.kickSusLen,
            sustainLevel=app.kickSusLev, release=app.kickR
            ),
        dB=app.kick_dB
        )
    return kick

def setSnare(app):
   
    snare = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=app.snareFreq,
            amp=app.snarePitchedAmp, wave=app.snarePitchedWave
            ),
        Oscillator(
            length=app.lengthOfCell, freq=None, amp=app.snareNoiseAmp, wave='whiteNoise'
            )
        ], 
        ADSR(
            length=app.lengthOfCell, attack=app.snareA, decay=app.snareD, 
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
    return snare

def setClHH(app):
    clHH = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=None, amp=app.clHHAmp, wave='whiteNoise'
            )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.clHHA,
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
    return clHH

def setOHH(app):
    oHH = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=None, amp=app.oHHAmp, wave='whiteNoise'
            )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.oHHA,
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
    return oHH

def setLoTom(app):
    loTom = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=app.loTomPitch, amp=app.loTomAmp,
            wave=app.tomWave
            )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.loTomA, decay=app.loTomD,
            sustainLength=app.loTomSusLen, sustainLevel=app.loTomSusLev,
            release=app.loTomR
            ) 
    )
    return loTom

def setHiTom(app): 
    hiTom = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=app.hiTomFreq, amp=app.hiTomAmp,
            wave=app.tomWave
        )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.hiTomA, decay=app.hiTomD,
            sustainLength=app.hiTomSusLen, sustainLevel=app.hiTomSusLev,
            release=app.hiTomR
            )
    )
    return hiTom
       
## SEQUENCER SCREEN ##

def sequencerScreen_onScreenActivate(app):
    app.stepi = 0
    app.playing = False
    app.sequencerButtons = []
    app.faders = []

    initializeSequences(app)
    loadSequencerBoard(app)
    initializeFaders(app)

def initializeSequences(app):
    app.sequenceLists = [
                    [False]*16,
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
    buttonW, xSpacing= 50, 5
    buttonH, ySpacing = 90, 10
    OGcx, cy = (app.width//15) + buttonW//2 ,  (app.height//8) + buttonH//2
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
        app.sequencerButtons += [rowOfButtons]
        cy += ySpacing + buttonH

def initializeFaders(app):
    ## KICK ##
    kickRow = app.sequencerButtons[0][-1]
    kickRowCY, kickRowLastX = kickRow.cy, (kickRow.leftX + kickRow.width)
    app.faders += Fader('volume',  )



def sequencerScreen_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='slateGray')
    drawLabel('DKTheThinker Proprietary DrumSynth', app.width/2, 20, 
              font='monospace', fill='indigo', bold=True, size=30)
    drawSequencer(app)
    drawFaders(app)


def drawSequencer(app):
    rows, cols = len(app.sequencerButtons), len(app.sequencerButtons[0])
    labels = ['kick', 'sanre', 'clHH', 'oHH', 'loTom', 'hiTom']
    for buttonRow in range(rows):
        buttonFamily = app.sequencerButtons[buttonRow][0]
        sequenceLabel = labels[buttonRow]
        labelX = buttonFamily.leftX - 5
        labelY = buttonFamily.topY + buttonFamily.height //2 
        drawLabel(sequenceLabel, labelX, labelY, align='right', font='obitron',
                  bold=True, size=16)
        for buttonCol in range(cols):
            if buttonCol == app.stepi and app.playing:
                borderColor = 'red'
            else: borderColor = 'black'
            app.sequencerButtons[buttonRow][buttonCol].drawButton(borderFill=borderColor)

def drawFaders(app):
    for fader in app.faders:
        fader.drawFader()

def sequencerScreen_onMousePress(app, mouseX, mouseY):
    checkAndHandleSequencerPress(app, mouseX, mouseY)
    
def sequencerScreen_onMouseDrag(app, mouseX, mouseY):
    for fader in app.faders:
        if fader.checkPressInFader(mouseX, mouseY):
            fader.moveFader(mouseY)

def sequencerScreen_onMouseRelease(app, mouseX, mouseY):
    for fader in app.faders:
        if fader.beingMoved:
            fader.updateValue()

    # checkClickInKnob(app, mouseX, mouseY)

# def checkClickInKnob:


# def sequencerScreen_onMouse:



def checkAndHandleSequencerPress(app, mouseX, mouseY):
    rows, cols = len(app.sequencerButtons), len(app.sequencerButtons[0])
    for row in range(rows):
        for col in range(cols):
            #get the pressed row and col of pressed button
            #update the corresponding row and col of app.sequenceLists
            app.sequencerButtons[row][col].checkPressInButton(mouseX, mouseY)
            app.sequenceLists[row][col] = app.sequencerButtons[row][col].pressed

def sequencerScreen_onKeyPress(app, key):
    if key == 'space':
        if app.playing == True:
            #reset the step index to 0 on every pause
            app.stepi = 0
        app.playing = not (app.playing)
    if key == 'k':
        app.kickFreq += 40
        app.samples['kick'] = setKick(app).getSamples()
        app.sequencer['kick'].oscillators = app.samples['kick']
        # post = app.samples['kick']
        # assert(pre == post)

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



        
def main():
    runAppWithScreens(initialScreen='sequencerScreen')

main()