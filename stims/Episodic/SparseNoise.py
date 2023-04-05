import json
import logging
import numpy as np
import zarr
from pathlib import Path
from psychopy import monitors, visual
from fitzhelpers.files import load_animal_info, load_port_num
from triggers import create_trigger

logging.basicConfig(level=logging.INFO)

expt_json = r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json'


stim_settings = {
    'num_trials': 2,
    'invert': 1,
    'stim_duration': 0.25,
    'inter_frame_interval': 0,# seconds
    'center_pos': [-13.1, 8],
    'image_size': [51, 51],
    'total_frames': 9000,
    'isi': 0,
    'initial_delay': 10,
    'head_angle': -12.5
}

trigger_type = 'SerialDaqOut'

data_path, animal_name = load_animal_info(expt_json)
if data_path is None or animal_name is None:
    raise ValueError('Datapath or animal name are invalid')

serial_port_name = load_port_num(expt_json)
if serial_port_name is None:
    raise ValueError('Unknown COM port None')

adjust_stim_duration_to_match_2p = False

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
                       color=[0, 0, 0], colorSpace=u'rgb')


sparse_noise = zarr.open(r'C:\Users\fitzlab1\Documents\psychopy\stims\Images/SparseNoise.zarr', 'r')[:stim_settings['total_frames'],:,:] 

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


frames_per_stim = np.round(stim_settings['stim_duration'] * stim_settings['frame_rate'])
isi_frames = np.round(stim_settings['isi']*stim_settings['frame_rate'])
stim_settings['frames_per_stim'] = 1 #frames_per_stim - changed trigger for only first frame
img = visual.ImageStim(win=my_win,
                       image=None,
                       mask=None,
                       units='deg',
                       color=[1, 1, 1], colorSpace=u'rgb', opacity=1,
                       size=stim_settings['image_size'],
                       pos = stim_settings['center_pos'],
                       ori = -stim_settings['head_angle'])
img.setAutoDraw(False)



#PreTrial Logging

expt_name = trigger.getNextExpName(data_path, animal_name)
stim_code_name = str(Path(__file__))
log_file = Path(data_path).joinpath(animal_name, f'{animal_name}.txt')
trigger.preTrialLogging(data_path,
                        animal_name,
                        expt_name,
                        stim_code_name,
                        [],
                        log_file)
stim_setting_path = str(Path(data_path).joinpath(animal_name, expt_name, 'stim_settings.json'))
trigger.logToFile(stim_setting_path,
                  json.dumps(stim_settings))


# Start Stim Presentations
if stim_settings['initial_delay'] > 0:
    logging.info('Waiting %0.1f seconds before starting stim to acquire a baseline.', stim_settings["initial_delay"])
    for _ in range(int(np.round(stim_settings['initial_delay']*stim_settings['frame_rate']))):
        my_win.flip()

for trial_num in range(stim_settings['num_trials']):
    logging.info('Starting Trial #%i', trial_num+1)
    trigger.preStim(1)
    if stim_settings['invert']:
        invert = (-1)**trial_num
    
    for frame_num, frame in enumerate(sparse_noise):
        img.setImage(frame * invert)
    
        img.setAutoDraw(True)
        
        trigger.preFlip(None)
        for _ in np.arange(frames_per_stim):
            my_win.flip()
        trigger.postFlip(None)

        img.setAutoDraw(False)
        for _ in np.arange(stim_settings['inter_frame_interval']*stim_settings['frame_rate']):
            my_win.flip()
        
    img.setAutoDraw(False)
    for _ in np.arange(isi_frames):
        my_win.flip()
    
    
    trigger.postStim(None)
    
    