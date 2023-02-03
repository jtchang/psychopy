from psychopy import visual, monitors, event
from psychopy.hardware import keyboard
from psychopy import core


contrastCounter = 0
flashInterval = 2       # interval for autonomous flashing
isUserControlled = 1 # If 1, the user can use "z" to flash the scrzzeen, 'c' to set to gray, 'x' to show a static grating


mon = monitors.Monitor('LGStim')
mon.setDistance(25)

my_win = my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=True,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True,
                       checkTiming=True,
                       winType='pyglet',
                       color=[-1,-1,-1])


# create visual stim:


stim = visual.Rect(win=my_win,
                   fillColor=[-1, -1, -1],
                   pos=[0, 0],
                   size=[360, 360],
                   units='deg',
                   autoLog=False)
stim.setAutoDraw(True)
gratingStim = visual.GratingStim(win=my_win, tex='sin', units='deg',
                                 pos=[0, 0], size=[300, 300], sf=0.06, autoLog=False)
gratingStim.setAutoDraw(False)

kb = keyboard.Keyboard()
face_color = [1, 1, 1]
if isUserControlled:
    while True:

        for key in kb.getKeys(['z', 'c', 'x', 'escape'], waitRelease=True):
            if key.name is 'x':
                gratingStim.setAutoDraw(not gratingStim.autoDraw)
            elif key.name is 'z':
                face_color = [-1, -1, -1] if face_color == [1, 1, 1] else [1, 1, 1]
                stim.setFillColor(face_color)
                gratingStim.setAutoDraw(False)
            elif key.name is 'c':
                gratingStim.setAutoDraw(False)
                stim.setFillColor([0, 0, 0])
            elif key.name is 'escape':
                core.quit()
        stim.draw()
        my_win.flip()


else:
    flip_auto_draw = True
    while True:
        clock = core.Clock()
        if flip_auto_draw:
            stim.setAutoDraw(not stim.autoDraw)
        while clock.getTime() < flashInterval:
            for key in kb.getKeys(['z', 'escape'], waitRelease=True):
                if key.name is 'z':
                    flip_auto_draw = not flip_auto_draw

                if key.name is 'escape':
                    core.quit()

            my_win.flip()
        else:
            stim.setContrast(-1,)
            my_win.flip()
            clock.reset()
