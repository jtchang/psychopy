import random
import numpy as np
import logging
import json
from pathlib import Path
from psychopy import visual, monitors
from fitzhelpers.gratings import makeGratingTexture
from fitzhelpers.files import load_animal_info, load_port_num
from triggers import create_trigger
from itertools import product
logging.basicConfig(level=logging.INFO)

expt_json = r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json'

stim_settings = {
    'num_trials': 5,
    'num_orientations': 8,
    'do_blank': 1,
    'num_blanks': 1,
    'initial_delay': 10,
    'stim_duration': 4,
    'isi': 6,
    'is_random': 0,
    'random_phase': 0,
    'temporal_freq': 1,
    'spatial_freqs': [0.015, 0.03, 0.06, 0.09, 0.12, 0.18, 0.21, 0.24, 0.27, 0.32],
    'contrast': 1,
    'texture_type': 'sqr',
    'change_direction_at': 1,
    'animal_orientation': 0,
    'center_pos': [0, 0],
    'stim_size': [360, 360]
}

trigger_type = 'SerialDaqOut'


data_path, animal_name = load_animal_info(expt_json)
if data_path is None or animal_name is None:
    raise ValueError('Datapath or animal name are invalid')

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
                       allowStencil=True)


# Create Trigger:
trigger = create_trigger(trigger_type,
                         data_path,
                         animal_name,
                         serial_port_num=serial_port_name
                         )


# Stim Setup
stim_settings['frame_rate'] = 1/my_win.monitorFramePeriod
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')

if adjust_stim_duration_to_match_2p:
    stim_settings['stim_duration'] = trigger.extendStimDurationToFrameEnd(stim_settings['stim_duration'])
logging.info(f'Stim Duration: {stim_settings["stim_duration"]}')

stim_settings['stim_frames'] = int(np.round(stim_settings['stim_duration'] * stim_settings['frame_rate']))
isi_frames = int(np.round(stim_settings['isi'] * stim_settings['frame_rate']))

rad_per_frame = 2*np.pi/ stim_settings['frame_rate'] #2*np.pi * stim_settings['temporal_freq'] / stim_settings['frame_rate']
change_direction_frame = int(np.round(stim_settings['stim_frames'] * stim_settings['change_direction_at']))

# Create Stim Ordering


orientations = np.arange(0, 360, 360.0/stim_settings['num_orientations'])
sfs = stim_settings['spatial_freqs']
stim_codes = list(product(orientations,sfs))


total_stims = len(stim_codes)+(stim_settings['num_blanks']*stim_settings['do_blank'])
num_trials = stim_settings['num_trials']

if stim_settings['random_phase']:
    starting_phases = np.random.rand(num_trials, total_stims) 
else:
    starting_phases = np.zeros((num_trials, total_stims))
stim_settings['starting_phase'] = starting_phases.tolist()


trial_ordering = np.empty((num_trials, total_stims), dtype=int)
stim_ids = np.arange(0, total_stims, 1, dtype=int)


for idx in range(num_trials):
    random.shuffle(stim_ids)
    trial_ordering[idx, :] = stim_ids


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
                                  sf=0,
                                  autoLog=False)



#PreTrial Logging

expt_name = trigger.getNextExpName(data_path, animal_name)
stim_code_name = str(Path(__file__))
log_file = Path(data_path).joinpath(animal_name, f'{animal_name}.txt')
trigger.preTrialLogging(data_path,
                        animal_name,
                        expt_name,
                        stim_code_name,
                        orientations,
                        log_file)
stim_setting_path = str(Path(data_path).joinpath(animal_name, expt_name, 'stim_settings.json'))
trigger.logToFile(stim_setting_path,
                  json.dumps(stim_settings))

# Start Stim Presentations
if stim_settings['initial_delay'] > 0:
    logging.info(f'Waiting {stim_settings["initial_delay"]} seconds before starting stim to acquire a baseline.')
    for _ in range(int(np.round(stim_settings['initial_delay']*stim_settings['frame_rate']))):
        my_win.flip()


for trial_num, stim_order in enumerate(trial_ordering):
    logging.info('Beginning Trial %i', trial_num+1)
    
    for stim_num in stim_order:
        grating_stim.setAutoDraw(True)
       
        phase = starting_phases[trial_num, stim_num]

        if stim_num < len(stim_codes):  # grating stims
            grating_stim.contrast = stim_settings['contrast']
            grating_stim.sf = stim_codes[stim_num][1]

            grating_stim.ori = stim_codes[stim_num][0] + ori_shift_val + stim_settings['animal_orientation']
            logging.info('Stim %i: %0.1f deg- SF: %0.2f  (phase = %0.2f)',
                         stim_num+1, stim_codes[stim_num][0], stim_codes[stim_num][1], phase)
            

            
        else:  # blank stims
            grating_stim.setContrast(0)
            logging.info('Stim %i (blank)', stim_num+1)

        trigger.preStim(stim_num+1)
        for frame_idx in range(stim_settings['stim_frames']):

            if frame_idx < change_direction_frame:
                phase_offset = frame_idx /stim_settings['frame_rate']
            else:
                phase_offset = rad_per_frame * (2 * change_direction_frame - frame_idx)
            grating_stim.setPhase(phase + phase_offset) 

            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)


        grating_stim.setAutoDraw(False)

        for _ in range(isi_frames):
            
            my_win.flip()
            
        
        trigger.postStim(None)
        
trigger.wrapUp(log_file, expt_name)
print('Finished all stimuli.')
    