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

GRADING INFO
Move faders to modify paramaters of sound
Press white buttons to add sound there
Space bar / play pause button will play the sequencer
Press 0 - Clears the sequence
Press 1 - Latin Groove
Press 2 - Rock Groove

References: 
Used Ideas from https://plainenglish.io/blog/making-a-synth-with-python-oscillators-2cb8e68e9c3b, 
    #https://github.com/18alantom/synth/blob/main/Code%20Oscillators.ipynb 
    Both of the above are from the same guy, 'Alan'
    I studied Alan's general approach to synthesis just to familarize myself
    how python handels audio and what not. But I implemented my own archetecure
    of synthesis. However, i did borrow a couple of functions for data 
    conversion and what not (turning sine values into data writeable to sepeakers).

Referecend https://antreith.wordpress.com/2018/05/12/elementary-signal-generation-with-python/ 
    and https://www.brownnoiseradio.com/resources/generating-white-noise-in-python%3A-a-step-by-step-guide
    For wave and white noise generation

Referenced https://docs.python.org/3/library/threading.html and
    https://realpython.com/intro-to-python-threading/
    These helped me learn what threading is, how it works, and how to implement
    it

Referenced https://people.csail.mit.edu/hubert/pyaudio/
    To learn how to use pyaudio module

Referenced https://spotify.github.io/pedalboard/
    For using the spotify pedalBoard module, specifically my filter feature is 
    the filter pedal from that library.

Referenced https://numpy.org/doc/stable/reference/index.html#reference 
    For using numpy arrays and what not

Unsuccessfuly tried to consult ChatGPT for help with debugging the modules i was
    unfamiliar with, but at the end of the day it's easier to just read the docs
    and figure it out myslf.
'''

def onAppStart(app):
    app.width = 1280
    app.height = 720
    setOnStepFromBPM(app)
    initializeSoundParamaters(app)
    loadSamples(app)

def setOnStepFromBPM(app):
    secondsPerBeat = 60/Sequencer.bpm
    app.lengthOfCell = (secondsPerBeat / 16) * sampleRate
    app.stepsPerSecond = 4 / secondsPerBeat #4 1/16 notes per beat

def initializeSoundParamaters(app): #Giant function that sets sound properties

    app.kickFreq = 100
    app.kickAmp = 1    #int <= 1
    app.kickWaveType = 'sine' #String
    app.kickA = 0.01
    app.kickD = .4
    app.kickSusLen = .1
    app.kickSusLev = .4
    app.kickR = .1
    app.kickVol = 2

    app.snareFreq = 200
    app.snarePitchedAmp = 1
    app.snarePitchedWave = 'triangle'
    app.snareNoiseAmp = .1
    app.snareA = .1
    app.snareD = .3
    app.snareSusLen = .2
    app.snareSusLev = 1
    app.snareR = .4
    app.snareVol = 1
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
    app.clHHFilterDrive = 1
    app.clHHVol = 1

    app.oHHAmp = 1
    app.oHHA = .01
    app.oHHD = 0
    app.oHHSusLen = .4
    app.oHHSusLev = 1
    app.oHHR = .09
    app.oHHFilterFreq = 7000
    app.oHHFilterRes = .4
    app.oHHFilterDrive = 8
    app.oHHVol = 1

    app.tomWave = 'square'
    app.loTomFreq = 220
    app.loTomAmp = .2
    app.loTomA = .01
    app.loTomD = .1
    app.loTomSusLen = .2
    app.loTomSusLev = .4
    app.loTomR = .5
    app.loTomCutoff = 200
    app.loTomRes = .1
    app.loTomDrive = 4
    app.loTomVol = 1

    app.hiTomFreq = 420
    app.hiTomAmp = .2
    app.hiTomA = .01
    app.hiTomD = .1
    app.hiTomSusLen = .2
    app.hiTomSusLev = .4
    app.hiTomR = .5
    app.hiTomCutoff = 200
    app.hiTomRes = .2
    app.hiTomDrive = 2
    app.hiTomVol = 1

def loadSamples(app):
    app.samples = {}
    # The list of master samples is formed here
    app.samples['kick'] = setKick(app).getSamples()
    app.samples['snare'] = setSnare(app).getSamples()
    app.samples['clHH'] = setClHH(app).getSamples()
    app.samples['oHH'] = setOHH(app).getSamples()
    app.samples['loTom'] = setLoTom(app).getSamples()
    app.samples['hiTom'] = setHiTom(app).getSamples()

# The following 'set_' functions generate 'DrumSynth' objects
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
        vol=app.kickVol
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
        vol=app.snareVol
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
        vol=app.clHHVol
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
        vol=app.oHHVol
        )
    return oHH

def setLoTom(app):
    loTom = DrumSynth(
        [
        Oscillator(
            length=app.lengthOfCell, freq=app.loTomFreq, amp=app.loTomAmp,
            wave=app.tomWave
            )
        ],
        ADSR(
            length=app.lengthOfCell, attack=app.loTomA, decay=app.loTomD,
            sustainLength=app.loTomSusLen, sustainLevel=app.loTomSusLev,
            release=app.loTomR
            ),
        pb.LadderFilter(
            mode=pb.LadderFilter.Mode.HPF12,
            cutoff_hz=app.loTomCutoff, resonance=app.loTomRes,
            drive=app.loTomDrive),
        vol = app.loTomVol
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
            ),
        pb.LadderFilter(
            mode=pb.LadderFilter.Mode.HPF12,
            cutoff_hz=app.hiTomCutoff, resonance=app.hiTomRes,
            drive=app.hiTomDrive),
        vol=app.hiTomVol
    )
    return hiTom
       
# UPDATE VALUE HELPERS #
# This might be bad style? but if the functions weren't here, they'd be burried
# in the Fader class so I think it is cleaner to have the functions here.
def changeBPM(app, val):
    Sequencer.bpm = val
    setOnStepFromBPM(app)
def changeKickVol(app, val):
    app.kickVol = val
def changeKickFreq(app, val):
    app.kickFreq = val
def changeSnareVol(app, val):
    app.snareVol = val
def changeSnarePitch(app, val):
    app.snarePitchedFreq = val
def changeSnarePitchedAmp(app, val):
    app.snarePitchedAmp = val
def changeClHHVol(app, val):
    app.clHHVol = val
def changeClHHFilterFreq(app, val):
    app.clHHFilterFreq = val
def changeClHHFilterRes(app, val):
    app.clHHFilterRes = val
def changeClHHFilterDrive(app, val):
    app.clHHFilterDrive = val
def chagneOHHVol(app, val):
    app.oHHVol = val
def changeOHHCFilterFreq(app, val):
    app.oHHFilterFreq = val
def changeOHHFilterRes(app, val):
    app.oHHFilterRes = val
def changeLoTomVol(app, val):
    app.loTomVol = val
def changeLoTomPitch(app, val):
    app.loTomFreq = val
def changeLoTomCutoff(app, val):
    app.loTomCutoff = val
def changeLoTomRes(app, val):
    app.loTomRes = val
def changeLoTomDrive(app, val):
    app.loTomDrive = val
def changeHiTomVol(app, val):
    app.hiTomVol = val
def changeHiTomPitch(app, val):
    app.hiTomFreq = val
def changeHiTomCutoff(app, val):
    app.hiTomCutoff = val
def changeHiTomRes(app, val):
    app.hiTomRes = val
def changeHiTomDrive(app, val):
    app.hiTomDrive = val

###### SEQUENCER SCREEN ######

# MODEL #
def sequencerScreen_onScreenActivate(app):
    app.stepi = 0
    app.playing = False
    app.sequencerButtons = []
    app.faders = []
    app.sequenceLists = [
                [False]*16,
                [False]*16,
                [False]*16,
                [False]*16,
                [False]*16,
                [False]*16
                ]

    initializeSequences(app)
    loadSequencerBoard(app)
    initializeFaders(app)
    initializeButtons(app)

def initializeButtons(app):
    app.buttons = []

    ## PLAY PAUSE ##
    playPause = Button(85+25, 50, 50, 50, onColor='red', offColor='white',
                       name='playPause')
    app.buttons.append(playPause )

def initializeSequences(app):

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
    # This function is probably in bad style, but the other approach would be
    # to have a list of all the arguments and then loop through that list, which
    # is unclear in its own right. This way you see every fader thats being 
    # added.
    app.faders.append(
        Fader('0 BPM', 165, 50, 40, 70,  40, 200,
              Sequencer.bpm, changeBPM)
    )

    faderW, faderH = 20, 80
    faderSpacing = 20

    ## KICK ##
    kickRow = app.sequencerButtons[0][-1]
    cy, cx = kickRow.cy, (kickRow.leftX + kickRow.width + faderW)
    app.faders.append(
        Fader('kick Vol', cx, cy, faderW, faderH,
              0, 3, app.kickVol, changeKickVol))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('kick Pitch', cx, cy, faderW, faderH,
              60, 220, app.kickFreq, changeKickFreq))
    
    ## SNARE ##
    snareRow = app.sequencerButtons[1][-1]
    cy, cx = snareRow.cy, (snareRow.leftX + snareRow.width + faderW)
    app.faders.append(
        Fader('snare Vol', cx, cy, faderW, faderH,
              0, 3, app.snareVol, changeSnareVol)
              )
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('snare Tone', cx, cy, faderW, faderH, 0, 2, 
              app.snarePitchedAmp, changeSnarePitchedAmp)
              )
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('snare Pitch', cx, cy, faderW, faderH, 100, 600,
              app.snareFreq, changeSnarePitch)
              )
    
    ## CLHH ##
    clHHRow = app.sequencerButtons[2][-1]
    cy, cx = clHHRow.cy, (clHHRow.leftX + clHHRow.width + faderW)
    app.faders.append(
        Fader('clHH Vol', cx, cy, faderW, faderH, 0, 3, app.clHHVol,
              changeClHHVol))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('clHH Cutoff', cx, cy, faderW, faderH, 5000, 14000,
              app.clHHFilterFreq, changeClHHFilterFreq))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('clHH Resonacne', cx, cy, faderW, faderH, 0, 1, app.clHHFilterRes,
              changeClHHFilterRes))
  
    ## OHH #
    oHHRow = app.sequencerButtons[3][-1]
    cy, cx = oHHRow.cy, (oHHRow.leftX + oHHRow.width + faderW)
    app.faders.append(
        Fader('oHH Vol', cx, cy, faderW, faderH, 0, 3, app.oHHVol, chagneOHHVol))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('oHH Cutoff', cx, cy, faderW, faderH, 500, 14000,
              app.oHHFilterFreq, changeOHHCFilterFreq))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('oHH Resonance', cx, cy, faderW, faderH, 0, 1, app.oHHFilterRes,
              changeOHHFilterRes)
    )

    ## loTOM ##
    loTomRow = app.sequencerButtons[4][-1]
    cy, cx = loTomRow.cy, (loTomRow.leftX + loTomRow.width + faderW)
    app.faders.append(
        Fader('loTom Vol', cx, cy, faderW, faderH, 0, 2, app.loTomVol,
              changeLoTomVol)
        )
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('loTom Pitch', cx, cy, faderW, faderH, 100, 400, app.loTomFreq,
              changeLoTomPitch))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('loTom Cutoff', cx, cy, faderW, faderH, 80, 2000, app.loTomCutoff,
              changeLoTomCutoff))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('loTom Resonacne', cx, cy, faderW, faderH, 0, 1, app.loTomRes,
              changeLoTomRes))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('loTom Drive', cx, cy, faderW, faderH, 0, 20, app.loTomDrive,
              changeLoTomDrive))
    
    ## HI TOM ##
    hiTomRow = app.sequencerButtons[5][-1]
    cy, cx = hiTomRow.cy, (hiTomRow.leftX + hiTomRow.width + faderW)
    app.faders.append(
        Fader('hiTom Vol', cx, cy, faderW, faderH, 0, 2, app.hiTomVol,
              changeHiTomVol)
        )
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('hiTom Pitch', cx, cy, faderW, faderH, 400, 700, app.hiTomFreq,
              changeHiTomPitch))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('hiTom Cutoff', cx, cy, faderW, faderH, 200, 2000, app.hiTomCutoff,
              changeHiTomCutoff))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('hiTom Resonacne', cx, cy, faderW, faderH, 0, 1, app.hiTomRes,
              changeHiTomRes))
    cx += faderW + faderSpacing
    app.faders.append(
        Fader('hiTom Drive', cx, cy, faderW, faderH, 0, 20, app.hiTomDrive,
              changeHiTomDrive))

# VIEW #
def sequencerScreen_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='slateGray')
    drawLabel('DKTheThinker Proprietary DrumSynth', app.width/2, 20, 
              font='monospace', fill='indigo', bold=True, size=30)
    drawSequencer(app)
    drawFaders(app)
    drawButtons(app)
    drawGradingText(app)

def drawButtons(app):
    for button in app.buttons:
        button.drawButton(borderFill='black')
        if button.name == 'playPause':
            if button.pressed:
                # DRAW PAUSE
                drawRect(button.cx-10, button.cy-15, 5, 30)
                drawRect(button.cx+5, button.cy-15, 5, 30)
            else:
                # DRAW PLAY 
                points = [button.cx-10, button.cy-15,
                          button.cx-10, button.cy+15,
                          button.cx+10, button.cy]
                drawPolygon(*points)

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

def drawGradingText(app):
    text = '''GRADING INFO
Move faders to modify paramaters of sound
Press white buttons to add sound at that step
Space bar / play pause button will play the sequencer
Press 0 - Clears the sequence
Press 1 - Latin Groove
Press 2 - Rock Groove
'''
    x, y = app.width-20, 10
    for line in text.splitlines():
        drawLabel(line, x, y, size=14, align='top-right')
        y += 20

# CONTROLLER #
def sequencerScreen_onMousePress(app, mouseX, mouseY):
    checkAndHandleSequencerPress(app, mouseX, mouseY)
    for button in app.buttons:
        if button.checkPressInButton(mouseX, mouseY):
            if button.name == 'playPause':
                if app.playing == False:
                    #reset the step index to 0 on every play
                    app.stepi = 0
                # app.buttons[0].pressed = not app.buttons[0].pressed
                app.playing = not (app.playing)
            
def sequencerScreen_onMouseDrag(app, mouseX, mouseY):
    for fader in app.faders:
        if fader.checkPressInFader(mouseX, mouseY):
            fader.moveFader(mouseY)

def sequencerScreen_onMouseRelease(app, mouseX, mouseY):

    for fader in app.faders:
        if fader.beingMoved:
            fader.updateValue(app)
            if fader.name.startswith('kick'):
                app.samples['kick'] = setKick(app).getSamples()
                
            elif fader.name.startswith('snare'):
                app.samples['snare'] = setSnare(app).getSamples()

            elif fader.name.startswith('clHH'):
                app.samples['clHH'] = setClHH(app).getSamples()
            
            elif fader.name.startswith('oHH'):
                app.samples['oHH'] = setOHH(app).getSamples()

            elif fader.name.startswith('loTom'):
                app.samples['loTom'] = setLoTom(app).getSamples()

            elif fader.name.startswith('hiTom'):
                app.samples['hiTom'] = setHiTom(app).getSamples()

            initializeSequences(app)

            fader.beingMoved = not fader.beingMoved

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
        #change the state of play pause button to match space bar
        app.buttons[0].pressed = not app.buttons[0].pressed
        if app.playing == False:
            #reset the step index to 0 on every play
            app.stepi = 0
        app.playing = not (app.playing)
    if key.isdigit():
        loadPreset(app, key)

def loadPreset(app, key):
    # digits either wipe or change the preset of the board
    if key == '0':
        #Clear board
        app.sequenceLists = [
            [False]*16,
            [False]*16,
            [False]*16,
            [False]*16,
            [False]*16,
            [False]*16
            ]
    elif key == '1':
        #LATIN GROOVE
        app.sequenceLists = [
            [True, False, False, False]*4,
            [False, False, False, True, False, False, True, False]*2,
            [True, False, False, True]*4,
            [False, False, True, False]*4,
            [False, False, False, True, False, False, True, False, False,
                False, False, False, True, False, False, False],
            [True, False, False, False, False, False, False, False, False,
                False, True, False, False, False, False, False]
            ]
    elif key == '2':
        # Rock groove
        app.sequenceLists = [
            [True, False, False, False, False, False, False, False]*2,
            [False, False, False, False, True, False, False, False]*2,
            [True, False, True, False]*4,
            [False]*16,
            [False]*16,
            [False]*16
        ]
    
    initializeSequences(app)
    # This block graphically changes the buttons on the sequencer
    rows, cols = len(app.sequencerButtons), len(app.sequencerButtons[0])
    for row in range(rows):
        for col in range(cols): 
            app.sequencerButtons[row][col].pressed = app.sequenceLists[row][col]

def sequencerScreen_onStep(app):
    if app.playing:
        for sequence in app.sequencer:
            app.sequencer[sequence].handleStep(app.stepi)
        app.stepi = (app.stepi+1) % 16 # %16 for beat wraparound

def main():
    runAppWithScreens(initialScreen='sequencerScreen')

main()