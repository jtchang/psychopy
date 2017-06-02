from psychopy import visual, core, monitors, tools,event
import random, sys,  itertools, math
from os import path

print "initialized"

mon = monitors.Monitor('testMonitor')
mon.setDistance(25)


numTrials = 10
doBlank = 1
nBlank = 1







targetDeg= 15                               # degrees of visual space
targetFreq= 15                              # degrees/second

stimDuration = 10                           # seconds
isi = 5                                     # seconds
initialDelay= 1                            # seconds
isRandom = True
gliderType= "ThreePoint"                      # TwoPoint or ThreePoint
parity ='m1'                                 # 1 or m1
diverging= False                            # Diverging or Converging for three point



centerPoint = [0,0]
originalImageSize=[96, 54]
originalBoxSize= 1
orientations =[1,3,5,7]

targetPixels=int(round(tools.monitorunittools.deg2pix(targetDeg, mon)))
scale =  targetPixels/originalBoxSize

fps=targetDeg/targetFreq
frames= fps * stimDuration

moviepath='%sv2' % gliderType


win = visual.Window([1920,1080], units='pix', monitor= mon, fullscr=False, screen=1, allowGUI=False, waitBlanking=False)


if frames >200:
    raise ValueError('The original movies did not have more than 200 frames') 

framerange = xrange(frames) if not diverging or gliderType=="TwoPoint" else reversed(xrangeframes)

clock = core.Clock()

stimNumber= 2*len(orientations) + 2 * doBlank
if doBlank:
    blankID= len(orientations)+1

if initialDelay >0:
    print " ".join(("waiting", str(initialDelay), "seconds before starting stim to acquire a baseline."))
    while clock.getTime()<initialDelay:
        win.flip()

image = visual.ImageStim(win=win, name='image',units='pix', opacity=1, interpolate=False)
image.setAutoDraw(True)


for stimID,orientation in sorted(enumerate(range(1,stimNumber,2)), key=lambda x: random.random() if isRandom else x):
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
                win.flip()
        image.setAutoDraw(False)
    else:
        print "Showing Blank"
        for fnum in framerange:
            clock.reset()
            while clock.getTime() < 1/fps:
                win.flip()
    clock.reset()
    while clock.getTime() < isi:
        win.flip()
print 'Finished all stimuli'
