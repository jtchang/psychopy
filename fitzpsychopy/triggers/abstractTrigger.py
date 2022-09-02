# Template for a triggering class.
# A triggering class must contain each of these functions.
# They can be empty / do nothing, but they must all be defined.
# Have a look at the noTrigger class for an example of a minimal implementation.

class trigger:
    def __init__(self, data_path=None, animal_name=None):
        """Template trigger code initializing"""
        self.data_path = data_path
        self.animal_name = animal_name

    def preStim(self, *args):
        """This code runs before each stim is displayed"""
        print(f'PreStim {args}')
        pass

    def postStim(self, *args):
        """This code runs after each stim is displayed"""
        pass

    def preFlip(self, *args):
        """this code runs before each stimulus frame is displayed"""
        pass

    def postFlip(self, *args):
        """This code runs after each stimulus frame is displayed"""
        pass

    def wrapUp(self, *args):
        """This code is run after all stimuli have"""
        print('This code is run after all stimuli have run.')
        pass

    def preTrialLogging(self, *args):
        """This code runs before trials"""
        pass

    def getNextExpName(self, *args):
        """This code finds information about the experiment"""
        return ""

    def logToFile(self, filename, data):
        pass

    def extendStimDurationToFrameEnd(self, stim_duration):
        """Matches stimulus time to the recording rate."""
        return stim_duration
