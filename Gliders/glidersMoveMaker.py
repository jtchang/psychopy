from psychopy import visual, core, monitors, tools,event
import random, sys,  itertools, math

import os
mon = monitors.Monitor('testMonitor')
mon.setDistance(25)
win = visual.Window([1920*4,1080*4], units='pix', monitor= mon, fullscr=False, screen=1, allowGUI=False, waitBlanking=False)


#--------------------------
#User Definable parameters 
#--------------------------

#Stimulus Parameters
cellDimInPix= 240                                #Dimensions of each cell in pixels
random.seed(9999)                               #seed the random number generator so that it is repeatable
gliderType='TwoPoint'                           #TwoPoint or Three Point glider?
diverging =False                                 #Is it diverging (True) or converging (False)- only applicable for 3 point gliders
orientations=4                                  #8 point (all neighbors), 4 point (cardinal directions), 2 point (horizontal) or 1 point (horizontal right)
framenumber=200
corrs=[1]



#Here's the section that does the math to figure out the size of the stimulus and also the number of frames needed

width= win.size[0] 
height= win.size[1]

columns= int(math.ceil(width/cellDimInPix))
rows= int(math.ceil(height/cellDimInPix))
#these two lists give the max & min x,y coordinates for our large boxes
wbound= [-1 *columns* cellDimInPix, columns *cellDimInPix]
hbound=[-1 *rows* cellDimInPix, rows *cellDimInPix]

if orientations == 8:
    orientationsList= range(1, orientations+1, 1)
elif orientations == 4:
    orientationsList= range(1, orientations*2 +1, 2)
elif orientations ==2:
    orientationsList= [3,7]
elif orientations ==1:
    orientationsList = [3]



def GenerateGliderFrame(win,wbound, hbound, cellDimInPix, prevFrame, type, orientation, corr):
    glider= [[0 for row in enumerate(xrange(hbound[0],hbound[1],cellDimInPix))] for col in enumerate(xrange(wbound[0],wbound[1],cellDimInPix))]
    for col, posx in enumerate(xrange(wbound[0], wbound[1], cellDimInPix)):
        for row, posy in enumerate(reversed(xrange(hbound[0], hbound[1], cellDimInPix))):
            if type == 'random' or not prevFrame:
                color= random.choice([-1, 1])
            elif type =='ThreePoint':
                if orientation == 1: # 0 degrees
                    xoffset = 0
                    yoffset = 1
                elif orientation == 2: # 45 degrees
                    xoffset = -1
                    yoffset = 1
                elif orientation == 3: # 90 degrees
                    xoffset = -1
                    yoffset = 0
                elif orientation == 4: # 135 degrees
                    xoffset = -1
                    yoffset = -1
                elif orientation == 5: # 180 degrees
                    xoffset = 0
                    yoffset = -1
                elif orientation == 6: # 225 degrees
                    xoffset = 1
                    yoffset = -1
                elif orientation == 7: # 270 degrees
                    xoffset = 1
                    yoffset = 0
                elif orientation == 8: #  315 degrees
                    xoffset = 1
                    yoffset = 1 
                x= col+xoffset
                y= row+yoffset                
                if 0 > x or x> len(xrange(wbound[0], wbound[1], cellDimInPix))-1 or 0 > y or y > len(xrange(hbound[0], hbound[1], cellDimInPix))-1:
                    color= random.choice([-1, 1])
                else:
                    color = prevFrame[x][y].fillColor[1] *prevFrame[col][row].fillColor[1] *corr
            elif type =='TwoPoint':
                if orientation == 1: # 0 degrees
                    xoffset = 0
                    yoffset = 1
                elif orientation == 2: # 45 degrees
                    xoffset = -1
                    yoffset = 1
                elif orientation == 3: # 90 degrees
                    xoffset = -1
                    yoffset = 0
                elif orientation == 4: # 135 degrees
                    xoffset = -1
                    yoffset = -1
                elif orientation == 5: # 180 degrees
                    xoffset = 0
                    yoffset = -1
                elif orientation == 6: # 225 degrees
                    xoffset = 1
                    yoffset = -1
                elif orientation == 7: # 270 degrees
                    xoffset = 1
                    yoffset = 0
                elif orientation == 8: #  315 degrees
                    xoffset = 1
                    yoffset = 1 
                x= col+xoffset
                y= row+yoffset                
                if 0 > x or x> len(xrange(wbound[0], wbound[1], cellDimInPix))-1 or 0 > y or y > len(xrange(hbound[0], hbound[1], cellDimInPix))-1:
                    color= random.choice([-1, 1])
                 
                else:
                    color = prevFrame[x][y].fillColor[1] *corr        
           
            glider[col][row] = visual.Rect(win, 
                            cellDimInPix,
                            cellDimInPix, 
                            fillColor=[color,color,color], 
                            lineColor=[color,color,color], 
                            pos=[posx, posy])
            
    return glider
    

def ShowGliderMovie(gliderMovie, fps):
    for idx,glider in enumerate(gliderMovie):
        t0= core.getTime()
        keypresses= event.getKeys()
        if ('escape' in keypresses):
            print('The User has exited the execution')
            sys.exit()
        #print 'showing frame # %i'% idx
        ShowGlider(glider, wbound, hbound, cellDimInPix)
        win.flip()
        win.getMovieFrame()
        core.wait(1.0/fps-(core.getTime()- t0)) #this is a hackish way to try to get as close to our wanted framerate as possible
        win.saveMovieFrames(filename)
       

def ShowGlider(glider, wbound, hbound, cellDimInPix):
    for i, posx in enumerate(xrange(wbound[0], wbound[1], cellDimInPix)):
        for j, posy in enumerate(xrange(hbound[0], hbound[1], cellDimInPix)):
            glider[i][j].draw()

def GenerateGliderMovie(win, wbound, hbound, cellDimInPix, gliderType, framenumber, orientation, corr, div):
    gliderMovie=[0 for i in xrange(framenumber)]

    for i in xrange(framenumber):
        if i ==0:
            gliderMovie[i]=GenerateGliderFrame(win,wbound, hbound, cellDimInPix,[], gliderType, orientation, corr) 
        else:
           
            gliderMovie[i]=GenerateGliderFrame(win,wbound, hbound, cellDimInPix, gliderMovie[i-1], gliderType, orientation, corr)
            
    if type== "ThreePoint" and div: #for the diverging case we cheat and just invert a converging movie
        gliderMovie=list(reversed(gliderMovie))
    return gliderMovie








#-------------------------
# Pregenerate the Stimuli
#-------------------------
print 'Generating the glider Movie'


for idx,pair in enumerate(itertools.product(corrs, orientationsList)):
    corrstring = str(pair[0]).replace('-', 'm')
    pathname = '%s' % (gliderType)
    
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    print 'Generating Movie #%i' % idx
    prevframe=[]
    for fnum in xrange(framenumber):
        frame=GenerateGliderFrame(win,wbound, hbound, cellDimInPix, prevframe, gliderType, pair[1], pair[0])
        filename='%s\Orientation%i_parity_%s_f%i.png' % ( pathname,pair[1], corrstring, fnum)
        ShowGlider(frame, wbound, hbound, cellDimInPix)
        win.flip()
        win.getMovieFrame()
        win.saveMovieFrames(filename)
        prevframe=frame
    




    

