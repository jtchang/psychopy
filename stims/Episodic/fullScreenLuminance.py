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
    'num_trials': 5,
    'initial_delay': 10,
    'lum_steps': 21,
    'stim_duration': 4,
    'isi': 4,
    'is_random':True,
    'drop_zero': True
}

trigger_type = 'SerialDaqOut'

data_path, animal_name = load_animal_info(expt_json)
if data_path is None or animal_name is None:
    raise ValueError('Datapath or animal name are invalid!')

serial_port_name = load_port_num(expt_json)
if serial_port_name is None:
    raise ValueError('Unknown COM port None')

adjust_stim_duration_to_match_2p = True

mon = monitors.Monitor('LGStim')
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
                   fillColor=[0,0,0],
                   autoDraw=True
                   )

# Stim Setup
stim_settings['frame_rate'] = my_win.getActualFrameRate(nWarmUpFrames=240)
logging.info(f'Frame Rate: {stim_settings["frame_rate"]:0.2f}')
lum_values = np.linspace(-1,1,stim_settings['lum_steps'])
stim_ids = np.arange(lum_values.shape[0])+1


# PreTrial Logging


expt_name = trigger.getNextExpName(data_path, animal_name)
logging.info(f'Animal Name: {animal_name}')
logging.info(f'Expt Num: {expt_name}')

stim_code_name = str(Path(__file__))
log_file = Path(data_path).joinpath(animal_name, f'{animal_name}.txt')
trigger.preTrialLogging(data_path,
                        animal_name,
                        expt_name,
                        stim_code_name,
                        lum_values,
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
    if stim_settings['is_random']:
        np.random.shuffle(stim_ids)
    logging.info('Starting Trial %i', trial_num + 1)

    for stim_id in stim_ids:
        stim.setAutoDraw(True)
        logging.info('Stim %i (%0.2f)', stim_id, lum_values[stim_id-1])
        stim.fillColor = np.ones(3)*lum_values[stim_id-1]

        trigger.preStim(stim_id)
        for _ in range(int(np.round(stim_settings['stim_duration']*stim_settings['frame_rate']))):
            trigger.preFlip(None)
            my_win.flip()
            trigger.postFlip(None)
        stim.fillColor=[0,0,0]
        for _ in range(int(np.round(stim_settings['isi']*stim_settings['frame_rate']))):
            my_win.flip()
        
            
        trigger.postStim(None)
        