import random
import numpy as np
import logging
import json
from pathlib import Path

from psychopy import visual, monitors, tools
from fitzhelpers.files import load_animal_info, load_port_num
from triggers import create_trigger

logging.basicConfig(level=logging.INFO)


expt_json = r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json'


stim_settings = {
    'num_trials': 20,
    'num_orientations': 4,
    'do_blank': 0,
    'num_blanks': 0,
    'initial_delay': 10,
    'stim_duration': 8,
    'isi': 0,
    'bar_color': [1, 1, 1],
    'invert': 1,
    'bar_width': 5,  # degrees
    'center_pos': [-960, 0],  # pixels
    'shuffle': 1,
    'head_angle': -26 #negative means rolled clockwise
}

# #Monitor Set Up
mon = monitors.Monitor('Stim1')
mon.setDistance(25)

my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=False,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=False,
                       color=[0, 0, 0],
                       pos=(0,0))

trigger_type = 'SerialDaqOut'

data_path, animal_name = load_animal_info(expt_json)
if data_path is None or animal_name is None:
    raise ValueError('Datapath or animal name are invalid')

serial_port_name = load_port_num(expt_json)
if serial_port_name is None:
    raise ValueError('Unknown COM port None')

adjust_stim_duration_to_match_2p = True


# Create Trigger:
trigger = create_trigger(trigger_type,
                         data_path,
                         animal_name,
                         serial_port_num=serial_port_name
                         )


stim_settings['frame_rate'] = my_win.getActualFrameRate(nWarmUpFrames=100)
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')

if adjust_stim_duration_to_match_2p:
    stim_settings['stim_duration'] = trigger.extendStimDurationToFrameEnd(stim_settings['stim_duration'])
logging.info(f'Stim Duration: {stim_settings["stim_duration"]}')

stim_settings['stim_frames'] = int(np.round(stim_settings['stim_duration'] * stim_settings['frame_rate']))
isi_frames = int(np.round(stim_settings['isi'] * stim_settings['frame_rate']))

# Setup Stim
bar_center = [tools.monitorunittools.pix2deg(stim_settings['center_pos'][0], mon),
                tools.monitorunittools.pix2deg(stim_settings['center_pos'][1], mon)]
bar = visual.Rect(win=my_win,
                  width=stim_settings['bar_width'],
                  height=360,
                  units='deg',
                  fillColor=stim_settings['bar_color'],
                  pos=bar_center)


#mon_diagonal = np.linalg.norm(np.array(mon.getSizePix()))
mon_diagonal = np.linalg.norm([1920, 1080])                  # hardcode this for the surround monitor
max_dim = tools.monitorunittools.pix2deg(mon_diagonal, mon) + stim_settings['bar_width']
stim_settings['angle_range'] = (-max_dim/2, max_dim/2)
deg_per_frame = max_dim / stim_settings['stim_frames']
orientations = np.arange(0, 360, 360.0/stim_settings['num_orientations']) 

# Set Stim Orders
stim_orders = np.empty((stim_settings['num_trials'], stim_settings['num_orientations']), dtype=int)
stim_ids = np.arange(stim_settings['num_orientations'])

for i in range(stim_orders.shape[0]):
    if stim_settings['shuffle']:
        random.shuffle(stim_ids)

    stim_orders[i, :] = stim_ids


ori_correction = -90


# PreTrial Logging

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

for trial_num, trial_order in enumerate(stim_orders):
    fill_color = np.array(stim_settings['bar_color']) * (-1 * stim_settings['invert'])**trial_num
    bar.setFillColor(fill_color)
    logging.info('Starting Trial %s', trial_num+1)
    for stim_num in trial_order:
        bar.setAutoDraw(True)
        theta = np.deg2rad(orientations[stim_num] + ori_correction - stim_settings['head_angle'])

        rot = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
        bar.setOri(np.rad2deg(theta))

        logging.info('Stim # %s : %0.2f', stim_num+1, orientations[stim_num])
        trigger.preStim(stim_num+1)
        for frame_num in range(stim_settings['stim_frames']):
            new_pos = np.array([-max_dim/2 + frame_num * deg_per_frame +bar_center[0], 0])
            rot_pos = np.dot(rot, new_pos)
            bar.setPos(rot_pos)
            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)

        bar.setAutoDraw(False)
        for _ in range(isi_frames):
            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)

        trigger.postStim(None)

trigger.wrapUp(log_file, expt_name)
print('Finished all stimuli.')
