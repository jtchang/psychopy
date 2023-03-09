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
    'num_orientations': 16,
    'do_blank': 0,
    'num_blanks': 0,
    'initial_delay': 1,
    'stim_duration': 8,
    'isi': 0,
    'bar_color': [1, 1, 1],
    'invert': 1,
    'bar_width': 5,  # degrees
    'spatial_freq': 0.09,
    'temporal_freq': 3,
    'center_pos': [0, 0],  # pixels
    'shuffle': 1,
    'head_angle': 0 #negative means rolled clockwise
}

# #Monitor Set Up
mon = monitors.Monitor('LGStim')
mon.setDistance(25)

stim_settings['deg_range'] = tools.monitorunittools.pix2deg(np.ceil(np.linalg.norm(mon.getSizePix())), mon)

my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=True,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True,
                       checkTiming=True,
                       allowStencil=True,
                       winType='pyglet',)

trigger_type = 'OutOnly'

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


stim_settings['frame_rate'] = 1/my_win.monitorFramePeriod
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')

if adjust_stim_duration_to_match_2p:
    stim_settings['stim_duration'] = trigger.extendStimDurationToFrameEnd(stim_settings['stim_duration'])
logging.info(f'Stim Duration: {stim_settings["stim_duration"]}')

stim_settings['stim_frames'] = int(np.round(stim_settings['stim_duration'] * stim_settings['frame_rate']))
isi_frames = int(np.round(stim_settings['isi'] * stim_settings['frame_rate']))

# Setup Stim
phase_per_frame = stim_settings['temporal_freq'] / stim_settings['frame_rate'] # modulus 1 per psychopy

bar_center = [tools.monitorunittools.pix2deg(stim_settings['center_pos'][0], mon),
                tools.monitorunittools.pix2deg(stim_settings['center_pos'][1], mon)]
bar_width =stim_settings['bar_width']
grating = visual.GratingStim(win=my_win,
                                  tex='sqr',
                                  units='deg',
                                  pos=bar_center,
                                  size = [360,360],
                                  sf=stim_settings['spatial_freq'],
                                  autoLog=False)

bar = visual.Aperture(win=my_win,
                           units='deg',
                           pos=bar_center,
                           size=1,
                           shape=[(-bar_width, 360),
                                           (-bar_width, -360),
                                           (bar_width, -360),
                                           (bar_width, 360)],
                           autoLog=False)




max_dim = stim_settings['deg_range'] + stim_settings['bar_width']/2
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

print(stim_orders)
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
    logging.info('Starting Trial %s', trial_num+1)
    
    for stim_num in trial_order:
        
        grating.setAutoDraw(True)
        bar.enable()
        theta = np.deg2rad(orientations[stim_num] + ori_correction - stim_settings['head_angle'])

        grating.ori = np.rad2deg(theta) + 90
        bar.ori = np.rad2deg(theta)
        rot = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
        

        logging.info('Stim: %i: %f', stim_num, np.rad2deg(theta))
        trigger.preStim(stim_num)
        for frame_num in range(stim_settings['stim_frames']):
            new_pos = np.array([-max_dim/2 + frame_num * deg_per_frame +bar_center[0], 0])
            rot_pos = np.dot(rot, new_pos)
            bar.setPos(rot_pos)

            if trial_num % 2 == 0 :
                phase_offset = frame_num * phase_per_frame 
            else:
                phase_offset = frame_num * -phase_per_frame
            grating.setPhase(phase_offset)
            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)


        grating.setAutoDraw(False)
        bar.disable()
        for _ in range(isi_frames):

            my_win.flip()


        trigger.postStim(None)

trigger.wrapUp(log_file, expt_name)
print('Finished all stimuli.')
