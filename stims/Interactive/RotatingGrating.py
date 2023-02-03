from psychopy import visual, core, monitors, event
from psychopy.hardware import keyboard
from psychopy.tools import monitorunittools
import time

#---------- Stimulus Description -----------#
'''This is an interactive RF mapping program with drifting gratings
Controls:
    Spatial Frequency: Numpad /,*
    Speed: Numpad +,-
    Reverse: R
    ON/OFF: Z
    Quit: Esc
    Reset: C
'''


mon = monitors.Monitor('LGStim')
mon.setDistance(25)

my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=True,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True,
                       checkTiming=True,
                       winType='pyglet',
                       units='deg')


grating_stim = visual.GratingStim(win=my_win,
                                  tex='sqr',
                                  pos=(0, 0),
                                  size=(360, 360),
                                  units='deg',
                                  mask='circle',
                                  ori=0,
                                  sf=0.06,
                                  phase=.25,
                                  autoDraw=True)


kb = keyboard.Keyboard()
mouse = event.Mouse(win=my_win)


frame_rate = 1/my_win.monitorFramePeriod
print(frame_rate)

ang_vel = 0.1  # Hz
while True:
    for key in kb.getKeys(waitRelease=True):
        if key.name is 'escape':
            core.quit()
        elif key.name is 'z':
            grating_stim.setAutoDraw(not grating_stim.autoDraw)
        elif key.name is 'r':
            ang_vel = ang_vel * -1
        elif key.name is 'num_add':
            ang_vel = ang_vel * 2
        elif key.name is 'num_subtract':
            ang_vel = ang_vel / 2
        elif key.name is 'num_divide':
            grating_stim.sf = grating_stim.sf / 2
        elif key.name is 'num_multiply':
            grating_stim.sf = grating_stim.sf * 2
        elif key.name is 'c':
            grating_stim.sf = 0.06
            grating_stim.phase = 0.25
            grating_stim.pos = (0, 0)
            ang_vel = 0.1

    buttons, times = mouse.getPressed(getTime=True)
    if buttons[0]:
        new_pos = mouse.getPos()
        grating_stim.setPos(new_pos)

    grating_stim.ori = (grating_stim.ori + 360 * ang_vel / frame_rate) % 360

    my_win.flip()
