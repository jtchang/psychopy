from os import path
from psychopy import visual, logging, core, filters, event, monitors, tools
import pylab
import math
import random
import numpy
import time
import imp
import sys
sys.path.append('../triggers')  # path to trigger classes
print('initialized')

#---------- Monitor Properties ----------#
mon = monitors.Monitor('stim2')  # gets the calibration for stimMonitor
mon.setDistance(25)
overwriteGammaCalibration = False
newGamma = 0.479


# stim properties
slowDownCoeff = 1  # 6
flipPolarity = 1  # Whether to flip polarity of stimulus after each repetition (used to make stimulus 'white')
waveletContrast = 20  # Can be 0,2,20,98
repeats = 4
interRepeatInt = 0  # time between repeats through the stims
movies = 10  # number of different wavelet movies to show
interMovieInt = 5  # in sec, time b/n movies, gray screen here
stimFramesPerTrial = 256  # number of images in each movie - should be 480. #256
# Movie is shown at 15 fps, so stim length=stimFramesPerTrial/30.


# Triggering type
# Can be any of:#'NoTrigger' - no triggering; stim will run freely
# 'SerialDaqOut' - Triggering by serial port. Stim codes are written to the MCC DAQ.
# 'OutOnly' - no input trigger, but does all output (to CED) and logging
# 'DaqIntrinsicTrigger' - waits for stimcodes on the MCC DAQ and displays the appropriate stim ID
#triggerType = 'DaqIntrinsicTrigger'
triggerType = 'SerialDaqOut'
serialPortName = 'COM3'  # ignored if triggerType is 'None'
adjustDurationToMatch2P = True

# Experiment logging parameters
dataPath = 'X:/'
animalName = 'F2654_2022-04-06'
logFilePath = dataPath+animalName+'\\'+animalName+'.txt'  # including filepath

# ---------- Stimulus code begins here ---------- #
stimCodeName = path.dirname(path.realpath(__file__))+'\\'+path.basename(__file__)
orientations = ''
mywin = visual.Window(monitor=mon, size=(1920, 1080), pos=[
                      0, 0], fullscr=False, screen=1, colorSpace='rgb255', color=(128., 128., 128.))

centerPoint = [-1920/4, 0]  # center of screen is [0,0] (degrees).
refresh_rate = 1/(mywin.getMsPerFrame(nFrames=240)[0]*1e-3)
num_draw_frames = int(numpy.round(refresh_rate//15))  # frames to draw per frame in movie
if overwriteGammaCalibration:
    mywin.setGamma(newGamma)
    print('Overwriting Gamma Calibration. New Gamma value: {newGamma}')
print('made window, setting up triggers')

# Set up the trigger behavior
trigger = None
if triggerType == 'NoTrigger':
    import noTrigger
    trigger = noTrigger.noTrigger(None)
elif triggerType == 'SerialDaqOut' or triggerType == 'OutOnly':
    import serialTriggerDaqOut
    print 'Imported trigger serialTriggerDaqOut'
    trigger = serialTriggerDaqOut.serialTriggerDaqOut(serialPortName)
    # determine the Next experiment file name
    expName = trigger.getNextExpName([dataPath, animalName])
    print 'Trial name: ', expName
    if triggerType == 'OutOnly':
        trigger.readSer = False
    # Record a bunch of serial triggers and fit the stim duration to an exact multiple of the trigger time
    if adjustDurationToMatch2P:
        print 'Waiting for serial Triggers'
    # store the stimulus data and prepare the directory
    trigger.preTrialLogging([dataPath, animalName, expName, stimCodeName, orientations, logFilePath])
    print('PreTrialLogging')
elif triggerType == 'DaqIntrinsicTrigger':
    import daqIntrinsicTrigger
    trigger = daqIntrinsicTrigger.daqIntrinsicTrigger(None)
else:
    print 'Unknown trigger type', triggerType


print('Window Made')
# make image stim
image = visual.ImageStim(win=mywin, name='image', units=u'pix',
                         pos=centerPoint, size=[2400, 2400],  # 1200
                         color=[1, 1, 1], colorSpace=u'rgb', opacity=1,
                         texRes=128, interpolate=True)
print 'testing'
clock = core.Clock()  # to track the time since experiment started
for rep in range(1, repeats+1):
    print 'Starting repetition '+str(rep)
    for tr in range(1, (movies+1)):
        print 'Starting wavelet movie '+str(tr)
        trigger.preStim(tr)

        image.setAutoDraw(True)
        for im in range(stimFramesPerTrial):
            Iname = 'C:/Users/fitzlab1/Documents/Psychopy/psychopy/Dan/wavelet/tiffDir_{}pctSat/wv'.format(
                waveletContrast)+str(tr)+'_' + '%04.0f' % (im+1) + '.tif'
            image.setImage(Iname)
            image.setContrast((-1)**(rep % (flipPolarity+1)))

            for frame_count in range(num_draw_frames):
                if frame_count == 0:
                    trigger.preFlip(None)
                mywin.flip()
                if frame_count == 0:
                    trigger.postFlip(None)

        # now do isi
        image.setAutoDraw(False)
        mywin.flip()
        trigger.postFlip(None)
        for _ in range(interMovieInt*refresh_rate-1):  # , time b/n movies, gray screen here
            # Keep flipping during the ISI. If you don't do this you can get weird flash artifacts when you resume flipping later.
            mywin.flip()
        trigger.postStim(None)


if triggerType != 'NoTrigger':
    trigger.wrapUp([logFilePath, expName])
print 'Finished all stimuli.'
