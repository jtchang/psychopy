import json
from pathlib import Path
import logging


def load_animal_info(filepath):
    if not Path(filepath).exists():
        logging.warning('Doesn''t exist')
        return None, None

    with open(filepath) as f:
        animal_info = json.load(f)

    datapath = animal_info.get('datapath', None)
    animal_name = animal_info.get('animal_name', None)

    return datapath, animal_name


def load_port_num(filepath):
    if not Path(filepath).exists():
        logging.warning('%s Doesn''t exist!', filepath)
        return None

    with open(filepath) as f:
        animal_info = json.load(f)

    return animal_info.get('com_port', None)
