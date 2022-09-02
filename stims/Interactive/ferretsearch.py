import random
import numpy as np
import logging
import json
from pathlib import Path
from psychopy import visual, monitors
from fitzhelpers.gratings import makeGratingTexture
from fitzhelpers.files import load_animal_info, load_port_num
from triggers import create_trigger
from itertools import count

logging.basicConfig(level=logging.INFO)

expt_json = r'C:/Users/jeremyc/documents/git/psychopy/animal_info.json'

stim_settings = {

    'num_orientations': 16,
    'stim_duration': 4,
    'isi': 6,
    'is_random': 1,
    'random_phase': 1,
    'temporal_freq': .25,
    'spatial_freq': 0.06,
    'contrast': 1,
    'texture_type': 'sqr',
    'change_direction_at': 1,
    'animal_orientation': 45,
    'center_pos': [0, 0],
    'stim_size': [360, 360]
}

trigger_type = 'NoTrigger'

data_path, animal_name = None, None

serial_port_name = load_port_num(expt_json)
if serial_port_name is None:
    raise ValueError('Unknown COM port None')

adjust_stim_duration_to_match_2p = True

# advanced stim settings (ignored if texture isn't lumSin or lumSqr)
stim_settings['maxv'] = 0.125
stim_settings['minv'] = 0.0
stim_settings['duty_cycle'] = 5
stim_settings['foreground_color'] = -1      # 1: black on white, -1: white on black


# Monitor Set Up
mon = monitors.Monitor('Desktop')
mon.setDistance(25)

my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=False,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True)


# Create Trigger:
trigger = create_trigger(trigger_type,
                         data_path,
                         animal_name,
                         serial_port_num=serial_port_name
                         )


# Stim Setup
stim_settings['frame_rate'] = my_win.getActualFrameRate(nWarmUpFrames=100)
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')

if adjust_stim_duration_to_match_2p:
    stim_settings['stim_duration'] = trigger.extendStimDurationToFrameEnd(stim_settings['stim_duration'])
logging.info(f'Stim Duration: {stim_settings["stim_duration"]}')

stim_settings['stim_frames'] = int(np.round(stim_settings['stim_duration'] * stim_settings['frame_rate']))
isi_frames = int(np.round(stim_settings['isi'] * stim_settings['frame_rate']))

rad_per_frame = 2*np.pi/ stim_settings['frame_rate'] #2*np.pi * stim_settings['temporal_freq'] / stim_settings['frame_rate']
change_direction_frame = int(np.round(stim_settings['stim_frames'] * stim_settings['change_direction_at']))

# Create Stim Ordering
total_stims = stim_settings['num_orientations']
stim_ids = np.arange(total_stims, dtype=int)
orientations = np.arange(0, 360, 360.0/stim_settings['num_orientations'])

# Create Grating
texture_type, ori_shift_val, background_texture = makeGratingTexture(stim_settings)

if background_texture is not None:
    bgrect = visual.PatchStim(win=my_win,
                              pos=stim_settings['center_pos'],
                              units='deg',
                              size=stim_settings['stim_size'],
                              tex=background_texture)
    bgrect.setAutoDraw(True)

grating_stim = visual.GratingStim(win=my_win,
                                  tex=texture_type,
                                  units='deg',
                                  pos=stim_settings['center_pos'],
                                  size=stim_settings['stim_size'],
                                  sf=stim_settings['spatial_freq'],
                                  autoLog=False)


for trial_num in count():
    logging.info('Beginning Trial %i', trial_num+1)
    if stim_settings['is_random']:
        random.shuffle(stim_ids)
        
    for stim_num in stim_ids:
        grating_stim.setAutoDraw(True)

        if stim_num < len(orientations):  # grating stims
            grating_stim.setContrast(stim_settings['contrast'])
            grating_stim.ori = orientations[stim_num] + ori_shift_val + stim_settings['animal_orientation']
            logging.info('Stim %i: %0.5f deg',
                         stim_num+1, orientations[stim_num])
        else:  # blank stims
            grating_stim.setContrast(0)
            logging.info('Stim %i (blank)', stim_num+1)

        trigger.preStim(stim_num+1)
        for frame_idx in range(stim_settings['stim_frames']):

            if frame_idx < change_direction_frame:
                phase_offset = frame_idx /stim_settings['frame_rate']
            else:
                phase_offset = rad_per_frame * (2 * change_direction_frame - frame_idx)
            grating_stim.setPhase(phase_offset) 

            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)


        grating_stim.setAutoDraw(False)
        for _ in range(isi_frames):
            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)
        
        trigger.postStim(None)

    