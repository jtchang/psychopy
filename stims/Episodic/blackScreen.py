
import json
from pathlib import Path
from psychopy import visual,  monitors
from fitzhelpers.files import load_animal_info
from triggers import create_trigger


print("initialized")


data_path, animal_name = load_animal_info(r'C:\Users\fitzlab1\Documents\psychopy\animal_info.json')


trigger_type = 'OutOnly'
serial_port_name = 'COM3'  # ignored if triggerType is "None"
adjustDurationToMatch2P = True


# ---------- Stimulus code begins here ---------- #

orientations = ''
# make stim
mon = monitors.Monitor('LGStim')
myWin = visual.Window(size=mon.getSizePix(), monitor=mon, fullscr=False, screen=1, allowGUI=False, waitBlanking=True)


stim = visual.PatchStim(myWin, tex="sqrXsqr", texRes=64,
                        size=[500, 500], sf=.0008, mask='none', pos=(1, 1))
stim.setAutoDraw(True)

stim.setColor(0, 'rgb255')
myWin.flip()

# load triggers


trigger = create_trigger(trigger_type,
                         data_path,
                         animal_name,
                         serial_port_num=serial_port_name)

expt_name = trigger.getNextExpName(data_path, animal_name)
stim_code_name = str(Path(__file__))
log_file = Path(data_path).joinpath(animal_name, f'{animal_name}.txt')
trigger.preTrialLogging(data_path,
                        animal_name,
                        expt_name,
                        stim_code_name,
                        orientations,
                        log_file)

print(f'Trial name: {expt_name}')
trigger.readSer = False


# just keep flipping forever
while True:
    myWin.flip()
