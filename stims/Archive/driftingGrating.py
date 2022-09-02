from psychopy import visual, core, monitors, tools
import random
import numpy
from os import path
from triggers import noTrigger, serialTriggerDaqOut, daqIntrinsicTrigger
print('initialized')

# Experiment logging parameters
dataPath = 'X:/'
animalName = 'F2709_2022-08-01'  # F2350_2019-07-10'

# ---------- Stimulus Description ---------- #
'''A fullscreen drifting grating for 2pt orientation tuning'''
#---------- Monitor Properties ----------#
mon = monitors.Monitor('Desktop')  # gets the calibration for stimMonitor
mon.setDistance(25)
overwriteGammaCalibration = False
newGamma = 0.479
# make a window
myWin = visual.Window(size=mon.getSizePix(), monitor=mon, fullscr=False, screen=1, allowGUI=False, waitBlanking=True)
frame_rate = myWin.getActualFrameRate()
print(f'Frame Rate: {frame_rate}')
# ---------- Stimulus Parameters ---------- #
# trials and duration
animalOrientation = 0
numOrientations = 16  # 8 #typically 4, 8, or 16#

orientations = numpy.arange(0, 360, 360.0/numOrientations)

numTrials = 10  # - Run all the stims this many times
doBlank = 1  # 0 for no blank stim, 1 to have a blank stim. The blank will have the highest stimcode.
nBlank = 1  # number of blanks to show per trial.gles.
changeDirectionAt = 1  # DO NOT SET TO 0!.
stimDuration = 4
isi = 6
isRandom = 1
initialDelay = 10  # 30- time in seconds to wait before first stimuli. Set to 0 to begin ASAP.
randomizePhase = 0
if randomizePhase:
    startingPhases = numpy.random.rand(numOrientations+doBlank*nBlank, numTrials)

# Grating parameter
temporalFreq = 1  # 1#1#1
spatialFreq = 0.015  # .015#.015#0.015#0.015#0.015#0.06 #15 #0.015
contrast = 1  # .6125#0.0125#0.05#1#0.0125
textureType = 'sqr'  # 'sqr' = square wave, 'sin' = sinusoidal,'sqrDutyCycle';
# Others: lumSin, lumSqr - these allow adjustment of min and max lum values

# Parameters for special textures
maxv = 0.125  # max lum of grating, range [0 1]; ignored unless textureType=lumSin or lumSqr
minv = 0.0  # min lum of grating, range [0 1]; ignored unless textureType=lumSin or lumSqr
dutyCycle = 5  # can be 1, 2, 3, 4, 6, 8,; # for sqrDutyCycle; Ignored otherwise
foregroundColor = -1  # 1=black on white; -1=white on black (eg small white); For dutyCycle, ignored otherwise

startingPhase = 0.0  # [initial phase for gratingStim
# aperture and position parameters
centerpos = tools.monitorunittools.pix2deg(myWin.size[0]/4, mon)  # 20#68 #visual degrees off by 2 (33.15 x 2)\
centerPoint = [0, 0]  # [0,0]
stimSize = [360, 360]  # [300,300]Size of grating in degrees

# Triggering type
# Can be any of:#'NoTrigger' - no triggering; stim will run freely
# 'SerialDaqOut' - Triggering by serial port. Stim codes are written to the MCC DAQ.
# 'OutOnly' - no input trigger, but does all output (to CED) and logging
# 'DaqIntrinsicTrigger' - waits for stimcodes on the MCC DAQ and displays the appropriate stim ID
# triggerType = 'OutOnly'
triggerType = 'NoTrigger'
serialPortName = 'COM3'  # ignored if triggerType is 'None'
adjustDurationToMatch2P = True

logFilePath = dataPath+animalName+'\\'+animalName+'.txt'  # including filepath

# ---------- Stimulus code begins here ---------- #
stimCodeName = path.dirname(path.realpath(__file__))+'\\'+path.basename(__file__)

if overwriteGammaCalibration:
    myWin.setGamma(newGamma)
    print(f'Overwriting Gamma Calibration. New Gamma value:{newGamma}')

print('made window, setting up triggers')
# Set up the trigger behavior
trigger = None
if triggerType == 'NoTrigger':
    trigger = noTrigger(None, None)
elif triggerType == 'SerialDaqOut' or triggerType == 'OutOnly':
    print('Imported trigger serialTriggerDaqOut')
    trigger = serialTriggerDaqOut(serialPortName)
    # determine the Next experiment file name
    expName = trigger.getNextExpName()
    print('Trial name: ', expName)
    if triggerType == 'OutOnly':
        trigger.readSer = False
    # Record a bunch of serial triggers and fit the stim duration to an exact multiple of the trigger time
    if adjustDurationToMatch2P:
        print('Waiting for serial Triggers')
        stimDuration = trigger.extendStimDurationToFrameEnd(stimDuration)
    # store the stimulus data and prepare the directory
    trigger.preTrialLogging([dataPath, animalName, expName, stimCodeName, orientations, logFilePath])
    if randomizePhase:
        numpy.savetxt(dataPath+animalName+'\\'+expName+'\\startingPhases.txt',
                      startingPhases, delimiter=',', fmt='%4.3f')
elif triggerType == 'DaqIntrinsicTrigger':
    trigger = daqIntrinsicTrigger(None)
else:
    print('Unknown trigger type', triggerType)

print(stimDuration)
changeDirectionTimeAt = stimDuration * changeDirectionAt

# create grating stim
# first handle special textures:
# value needed to make requsted ori match Fitzlab convention (works for builtin Psychopy textures specified by string (eg 'sin')
orishiftVal = -90
if textureType == 'sqrDutyCycle':
    textureType = 1*numpy.ones((dutyCycle, 1))
    textureType[1, :] = -1
    orishiftVal = 0
    textureType = foregroundColor*textureType
elif textureType == 'lumSin':
    x = numpy.linspace(0, 2*numpy.pi, 256, False)[numpy.newaxis]
    x = x.T
    y = numpy.sin(x)
    y = (y+1.0)/2.0  # now on 0..1 range
    nr = numpy.array([minv, maxv])
    nr = nr*2-1  # now converted to desired -1 1 range
    rg = nr[1]-nr[0]
    y = y*rg+nr[0]  # y is now in the -1 to 1 range, adjusted to match requested min and max
    textureType = y
    orishiftVal = 0
    clr = (nr[0]+nr[1])/2
    #clr = clr[0]
    barTexture = clr*numpy.ones([256, 256, 3])
    bgrect = visual.PatchStim(win=myWin, pos=centerPoint, size=stimSize, units='deg', tex=barTexture)
    bgrect.setAutoDraw(True)
elif textureType == 'lumSqr':
    nr = numpy.array([minv, maxv])[numpy.newaxis]
    nr = nr*2-1  # now converted to desired -1 1 range
    nr = nr.T
    textureType = nr
    orishiftVal = 0
    clr = (nr[0]+nr[1])/2
    #clr = clr[0]
    barTexture = clr*numpy.ones([256, 256, 3])
    bgrect = visual.PatchStim(win=myWin, pos=centerPoint, size=stimSize, units='deg', tex=barTexture)
    bgrect.setAutoDraw(True)

# make the grating
gratingStim = visual.GratingStim(win=myWin, tex=textureType, units='deg',
                                 pos=centerPoint, size=stimSize, sf=spatialFreq, autoLog=False)
gratingStim.setAutoDraw(False)


barTexture = numpy.ones([256, 256, 3])
# lipStim = visual.PatchStim(win=myWin,tex=barTexture,mask='none',units='pix',pos=[-920,500],size=(100,100))
# flipStim.setAutoDraw(False)#up left, this is pos in y, neg in x
clrctr = 1

# run
clock = core.Clock()  # make one clock, instead of a new instance every time. Use
print(f'{len(orientations)+doBlank} stims will be run for {numTrials} trials.')
if nBlank > 1:
    print(f'Will run blank {nBlank} time(s)')
 # force a wait period of at least 5 seconds before first stim
if initialDelay > 0:
    print(f' waiting {initialDelay} seconds before starting stim to acquire a baseline.')
    while clock.getTime() < initialDelay:
        myWin.flip()
for trial in range(0, numTrials):
    # determine stim order
    print(f'Beginning Trial {trial+1}')
    stimOrder = numpy.arange(0, len(orientations)+doBlank)
    if nBlank > 1:
        blankID = len(orientations)
        for ibl in range(1, nBlank):
            stimOrder.append(blankID)
    if isRandom:
        random.shuffle(stimOrder)
    for stimNumber in stimOrder:
        if randomizePhase:
            startingPhase = startingPhases[stimNumber, trial]  # startingPhase = numpy.random.rand(1)
        gratingStim.setAutoDraw(True)

        trigger.preStim(stimNumber+1)

        if stimNumber == len(orientations):
            gratingStim.setContrast(0)
            print('\tStim', stimNumber+1, ' (blank)')
        else:
            gratingStim.setContrast(contrast)
            gratingStim.ori = orientations[stimNumber]+orishiftVal+animalOrientation
            print('\tStim', stimNumber+1, orientations[stimNumber], 'deg (phase=', startingPhase, ')')
        clock.reset()
        while clock.getTime() < stimDuration:
            clrctr = clrctr+1
            if clock.getTime() > changeDirectionTimeAt:
                gratingStim.setPhase(startingPhase+changeDirectionTimeAt*temporalFreq -
                                     (clock.getTime()-changeDirectionTimeAt)*temporalFreq)
            else:
                gratingStim.setPhase(startingPhase+clock.getTime()*temporalFreq)
            trigger.preFlip(None)
            myWin.flip()
            trigger.postFlip(None)

        if isi != 0:
            clock.reset()
            gratingStim.setAutoDraw(False)
            trigger.preFlip(None)
            myWin.flip()
            trigger.postFlip(None)
            while clock.getTime() < isi:
                myWin.flip()
        trigger.postStim(None)

trigger.wrapUp([logFilePath, expName])
print('Finished all stimuli.')
