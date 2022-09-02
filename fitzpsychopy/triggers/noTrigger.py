# No Triggering - A trigger class for when you want your stim to run freely, neither
# sending information nor receiving it.
from .abstractTrigger import trigger


class noTrigger(trigger):
    def __init__(self, data_path, animal_name, **kwargs):
        super().__init__(data_path, animal_name)

    def log_to_file(self, filename, data, **args):
        pass
