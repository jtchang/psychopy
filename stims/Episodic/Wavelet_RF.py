import logging
import numpy as np
import zarr
from psychopy import monitors, visual
from fitzhelpers.files import load_animal_info
from triggers import create_trigger

logging.basicConfig(level=logging.INFO)

data_path, animal_name = load_animal_info(r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json')


stim_settings = {
    'num_trials': 2,
    'invert': 1,
    'stim_duration': 0.25,  # seconds
    'center_pos': [0, 0],
    'image_size': [51, 51],
    'total_frames': 9000,
    'isi': 10
}


trigger_type = 'NoTrigger'
serial_port_name = 'COM3'
adjust_stim_duration_to_match_2p = True


mon = monitors.Monitor('Desktop')
mon.setDistance(25)


my_win = visual.Window(size=mon.getSizePix(),
                       monitor=mon,
                       fullscr=False,
                       screen=1,
                       allowGUI=False,
                       waitBlanking=True,
                       color=[0, 0, 0], colorSpace=u'rgb')


wavelet = zarr.open(r'Stims/Images/SparseNoise.zarr', 'r')[:stim_settings['total_frames'],:,:] 

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


frames_per_stim = np.round(stim_settings['stim_duration'] * stim_settings['frame_rate'])
isi_frames = np.round(stim_settings['isi']*stim_settings['frame_rate'])

img = visual.ImageStim(win=my_win,
                       image=None,
                       mask=None,
                       units='deg',
                       color=[1, 1, 1], colorSpace=u'rgb', opacity=1,
                       size=stim_settings['image_size'],
                       pos = stim_settings['center_pos'])
img.setAutoDraw(False)


for trial_num in range(stim_settings['num_trials']):
    trigger.preStim(1)
    if stim_settings['invert']:
        invert = (-1)**trial_num
    
    for frame_num, frame in enumerate(wavelet):
        img.setImage(frame * invert)
    
        img.setAutoDraw(True)
        
        trigger.preFlip(None)
        my_win.flip()
        trigger.postFlip(None)
        
        for _ in np.arange(frames_per_stim-1):
            my_win.flip()
   
    img.setAutoDraw(False)
    for _ in np.arange(isi_frames):
        my_win.flip()
    
    
    trigger.postStim(None)
    
    