from psychopy import visual, core, monitors, event
from psychopy.hardware import keyboard
from psychopy.tools import monitorunittools
import time

#---------- Stimulus Description -----------#
'''This is an interactive RF mapping program with drifting gratings'''


mon = monitors.Monitor('Desktop')
mon.setDistance(25)

my_win = visual.Window(size=mon.getSizePix(),
                       units='deg',
                       monitor=mon,
                       fullscr=False,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True)


grating_stim = visual.GratingStim(win=my_win,
                                  tex='sqr',
                                  pos=(0, 0),
                                  size=(20, 20),
                                  units='deg',
                                  mask='circle',
                                  sf=0.06,
                                  autoDraw=True)

kb = keyboard.Keyboard()
mouse = event.Mouse(win=my_win)

frame_rate = my_win.getActualFrameRate(nWarmUpFrames=90)
print(frame_rate)


movement_increment = 1
tf = 1  # Hz

log_pos = False

while True:

    for key in kb.getKeys(waitRelease=False):
        # Movement
        if key.name is 'num_8':
            grating_stim.setPos((grating_stim.pos[0], grating_stim.pos[1]+movement_increment))
            log_pos = True
        elif key.name is 'num_2':
            grating_stim.setPos((grating_stim.pos[0], grating_stim.pos[1]-movement_increment))
            log_pos = True
        elif key.name is 'num_6':
            grating_stim.setPos((grating_stim.pos[0]+movement_increment, grating_stim.pos[1]))
            log_pos = True
        elif key.name is 'num_4':
            grating_stim.setPos((grating_stim.pos[0]-movement_increment, grating_stim.pos[1]))
            log_pos = True
        elif key.name is 'num_divide':
            movement_increment = movement_increment / 2
            print('decreasing movment speed')
            log_pos = True
        elif key.name is 'num_multiply':
            print("Increasing movement speed")
            movement_increment = movement_increment * 2
            log_pos = True
        # Size
        elif key.name is 'num_subtract':
            grating_stim.setSize((grating_stim.size[0]-5, grating_stim.size[1]-5))
            log_pos = True
        elif key.name is 'num_add':
            grating_stim.setSize((grating_stim.size[0]+5, grating_stim.size[1]+5))
            log_pos = True
        # Spatial Frequency
        elif key.name is 'num_1':
            grating_stim.sf = grating_stim.sf/2
            log_pos = True
        elif key.name is 'num_3':
            grating_stim.sf = grating_stim.sf*2
            log_pos = True
        # Temporal Frequency
        elif key.name is 'num_0':
            tf = tf - 0.5 if tf >= 0.5 else tf
            log_pos = True
        elif key.code is 110:  # numpad period
            tf = tf + 0.5
            log_pos = True
        elif key.name is 'num_7':
            grating_stim.setOri(grating_stim.ori-10)
            log_pos = True
        elif key.name is 'num_9':
            grating_stim.setOri(grating_stim.ori+10)
            log_pos = True
        elif key.name is 'num_5':
            grating_stim.setOri(0)
            grating_stim.setPos((0, 0))
            grating_stim.setSize((25, 25))
            log_pos = True
        # Contrast
        elif key.name is 'down':
            new_contrast = grating_stim.contrast - 0.1
            if new_contrast < 0:
                new_contrast = 0
            grating_stim.setContrast(new_contrast)
            log_pos = True
        elif key.name is 'up':
            new_contrast = grating_stim.contrast + 0.1
            if new_contrast > 1:
                new_contrast = 1
            grating_stim.setContrast(new_contrast)
            log_pos = True
        # Quality of life
        elif key.name is 'x':
            grating_stim.setAutoDraw(not grating_stim.autoDraw)
            log_pos = True
        elif key.name is 'z':
            log_pos = True
        elif key.name is 'escape':
            core.quit()

    buttons, times = mouse.getPressed(getTime=True)
    if buttons[0]:
        new_pos = mouse.getPos()
        grating_stim.setPos(new_pos)
        if times[0] > 0.25:
            log_pos = True
        mouse.clickReset()
    if log_pos:
        deg_pos = grating_stim.pos
        pix_pos = monitorunittools.deg2pix(grating_stim.pos, mon)
        print(f"""
        ==========Grating Information==========
        Position: ({deg_pos[0]:0.2f}, {deg_pos[1]:0.2f}) degrees ({pix_pos[0]:0.2f}, {pix_pos[1]:0.2f})
        TF: {tf}
        SF: {grating_stim.sf}
        orientation: {grating_stim.ori}
        size: {grating_stim.size}
        contrast: {grating_stim.contrast:0.2f}
        ==============================""")
        log_pos = False

    my_win.flip()
