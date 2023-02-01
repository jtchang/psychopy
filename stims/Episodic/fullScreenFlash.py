import logging
import json
import numpy as np
from pathlib import Path
from psychopy import visual, monitors
from fitzhelpers.files import load_animal_info, load_port_num
from triggers import create_trigger


logging.basicConfig(level=logging.INFO)

expt_json = r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json'

stim_settings = {
    'num_trials': 20,
    'initial_delay': 10,
    'lum0': -1.0,
    'lum1': 1.0,
    'flash_interval': 10,
    'drop_zero': False
}


trigger_type = 'SerialDaqOut'

data_path, animal_name = load_animal_info(expt_json)
if data_path is None or animal_name is None:
    raise ValueError('Datapath or animal name are invalid!')


serial_port_name = load_port_num(expt_json)
if serial_port_name is None:
    raise ValueError('Unknown COM port None')

adjust_stim_duration_to_match_2p = True

# Monitor Set Up
mon = monitors.Monitor('Stim1')
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

stim = visual.Rect(win=my_win,
                   width=mon.getSizePix()[0],
                   height=mon.getSizePix()[1],
                   units='pix',
                   pos=my_win.pos,
                   fillColor=np.ones((3))*stim_settings['lum0'],
                   autoDraw=True
                   )

# Stim Setup
stim_settings['frame_rate'] = my_win.getActualFrameRate(nWarmUpFrames=100)
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')

# PreTrial Logging

expt_name = trigger.getNextExpName(data_path, animal_name)
stim_code_name = str(Path(__file__))
log_file = Path(data_path).joinpath(animal_name, f'{animal_name}.txt')
stim_settings['flash_interval'] = trigger.extendStimDurationToFrameEnd(stim_settings['flash_interval'])
trigger.preTrialLogging(data_path,
                        animal_name,
                        expt_name,
                        stim_code_name,
                        None,
                        log_file)
stim_setting_path = str(Path(data_path).joinpath(animal_name, expt_name, 'stim_settings.json'))
trigger.logToFile(stim_setting_path,
                  json.dumps(stim_settings))

# Start Stim Presentations
if stim_settings['initial_delay'] > 0:
    logging.info(f'Waiting {stim_settings["initial_delay"]} seconds before starting stim to acquire a baseline.')
    for _ in range(int(np.round(stim_settings['initial_delay']*stim_settings['frame_rate']))):
        my_win.flip()


for trial_num in range(stim_settings['num_trials']):
    logging.info('Starting Trial %i', trial_num+1)

    trigger.preStim(1)
    stim.fillColor = np.ones((3))*stim_settings['lum1']
    for _ in range(int(np.round(stim_settings['flash_interval']*stim_settings['frame_rate']))):
        trigger.preFlip(None)
        my_win.flip()
        trigger.postFlip(None)

    trigger.preStim(0)
    stim.fillColor = np.ones((3))*stim_settings['lum0']
    for _ in range(int(np.round(stim_settings['flash_interval']*stim_settings['frame_rate']))):
        trigger.preFlip(None)
        my_win.flip()
        trigger.postFlip(None)

    trigger.postStim(None)

trigger.wrapUp(log_file, expt_name)
print('Finished all Stimuli')
