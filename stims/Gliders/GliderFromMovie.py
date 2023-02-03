from psychopy import visual, core, monitors, tools,event
import random, sys,  itertools, math
from os import path
sys.path.append("../triggers")

print "initialized"

'''Fullscreen glider movie presentation'''

mon = monitors.Monitor('testMonitor')
mon.setDistance(25)


#Experiment logging parameters
dataPath='x:/'
animalName='F2078_2017-05-17'; 
logFilePath =dataPath+animalName+'\\'+animalName+'.txt' #including filepath
stimCodeName=path.dirname(path.realpath(__file__))+'\\'+path.basename(__file__)


numTrials = 10
doBlank = 1
nBlank = 1



targetDeg= 5                               # degrees of visual space
targetFreq= 5                              # degrees/second

stimDuration = 10                           # seconds
isi = 5                                     # seconds
initialDelay= 1                            # seconds
isRandom = True
gliderType= "ThreePoint"                      # TwoPoint or ThreePoint
parity ='m1'                                 # 1 or m1
diverging= True                            # Diverging or Converging for three point
headangle = 0                              #correction factor for head angle (+) rotates screen clockwise
randomizeMovie = False                       #choose a random starting point in each movie for every block

triggerType = 'Tester'

# Aperture settings
inAperture = True
aperturePosition = (50,50)
apertureSize= 400                           #for now in pixels
apertureShape = 'circle'


#Setup our original Movie parameters
centerPoint = [0,0]
originalImageSize=[96, 54]
originalBoxSize= 1
orientations =[1,3,5,7]



targetPixels=int(round(tools.monitorunittools.deg2pix(targetDeg, mon)))
scale =  targetPixels/originalBoxSize
print scale
fps=targetDeg/targetFreq
frames= fps * stimDuration

moviepath='%sv2' % gliderType


# Make Window, aperture if necessary, and setup triggers
win = my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=True,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True,
                       checkTiming=True,
                       winType='pyglet',
                       allowStencil=True)
if inAperture:
    aperture= visual.Aperture(win, size = apertureSize, pos=aperturePosition, shape = apertureShape)


print "made window, setting up triggers"
#Set up the trigger behavior
trigger = None
if triggerType == "NoTrigger":
    import noTrigger
    trigger = noTrigger.noTrigger(None) 
elif triggerType == "SerialDaqOut" or triggerType == 'OutOnly':
    import serialTriggerDaqOut
    print 'Imported trigger serialTriggerDaqOut'
    trigger = serialTriggerDaqOut.serialTriggerDaqOut(serialPortName) 
    # determine the Next experiment file name
    expName=trigger.getNextExpName([dataPath,animalName])
    print "Trial name: ",expName
    if triggerType == 'OutOnly':
        trigger.readSer=False
    #Record a bunch of serial triggers and fit the stim duration to an exact multiple of the trigger time
    if adjustDurationToMatch2P:
        print "Waiting for serial Triggers"
        stimDuration = trigger.extendStimDurationToFrameEnd(stimDuration)
    # store the stimulus data and prepare the directory
    trigger.preTrialLogging([dataPath,animalName,expName,stimCodeName,orientations,logFilePath])
elif triggerType=="DaqIntrinsicTrigger":
    import daqIntrinsicTrigger
    trigger = daqIntrinsicTrigger.daqIntrinsicTrigger(None) 
else:
    print "Unknown trigger type", triggerType


#Calculate the number of frames to iterate over

if frames >200:
    raise ValueError('The original movies did not have more than 200 frames') 
elif frames<2:
    raise ValueError('The fps and stimDuration you have choosen only displays one frame')     

 
framerange = list(reversed(range(frames)))if diverging and gliderType == "ThreePoint" else range(frames)


clock = core.Clock()


#figure out number of stims to do
stimNumber= 2*len(orientations) + 2 * doBlank
if doBlank:
    blankID= len(orientations)+1


#show blank screen if there is an initial delay
if initialDelay >0:
    print " ".join(("waiting", str(initialDelay), "seconds before starting stim to acquire a baseline."))
    while clock.getTime()<initialDelay:
        win.flip()


image = visual.ImageStim(win=win, name='image',units='pix', opacity=1, interpolate=False, ori= headangle)
image.setAutoDraw(True)


for block in xrange(numTrials):
    print "Staring Trial %i" % block
    
    if randomizeMovie:
        frameoffset=random.randrange(0, 200-frames)
        framerange = list(reversed(range(frameoffset, frames+frameoffset)))if diverging and gliderType == "ThreePoint" else range(frameoffset, frames+frameoffset)
        print "starting at frame %i" % frameoffset
    

    for stimID,orientation in sorted(enumerate(range(1,stimNumber,2)), key=lambda x: random.random() if isRandom else x):
        #trigger.preStim(stimID)
        if stimID <4:                           #Stimulus Trial
            image.setAutoDraw(True)
            print "Showing Orientation #%i" %orientation

            for fnum in framerange:
                
                paritystring = str(parity).replace('-', 'm')
                testImage='%s\Orientation%i_parity_%s_f%i.png' % (moviepath, orientation, paritystring, fnum)
                image.setImage(testImage)
                image.size=([x * scale for x in originalImageSize])
                clock.reset()
                while clock.getTime() < 1/fps:
                    #trigger.preFlip(None)
                    win.flip()
                    #trigger.postFlip(None)
            image.setAutoDraw(False)
        else:
            print "Showing Blank"
            for fnum in framerange:
                clock.reset()
                while clock.getTime() < 1/fps:
                    #trigger.preFlip(None)
                    win.flip()
                    #trigger.postFlip(None)
        clock.reset()
        while clock.getTime() < isi:
            #trigger.preFlip(None)
            win.flip()
            #trigger.postFlip(None)
        #trigger.postStim(None)    


trigger.wrapUp([logFilePath, expName])
print 'Finished all stimuli'
