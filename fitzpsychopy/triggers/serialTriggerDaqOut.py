# Triggers when data arrives at the serial port.
# Sends stimcodes via Measurement Computing DAQ.
import serial
import csv
import time
import math
import datetime
from psychopy import core
import mcculw.ul as UL
from mcculw.enums import DigitalPortType, DigitalIODirection
from .abstractTrigger import trigger
from os import path, makedirs
import shutil
import natsort
import re
from pathlib import Path
import logging
logger = logging.getLogger()
class serialTriggerDaqOut(trigger):

    def __init__(self, data_path=None, animal_name=None, serial_port_name = 'COM5', **kwargs):

        super().__init__(data_path, animal_name)
        logger.debug(serial_port_name)
        # serial port setup
        self.boardNum = kwargs.get('board_num', 0)
        self.serialPortName = serial_port_name

        self.ser = serial.Serial(self.serialPortName, 9600, timeout=0)
        self.basestate = 1  # what is baseline state? 1 if stimtrig is high to low, 0 if low to high
        self.readSer = True  # if false, it will trigger immediately, but will still log data

        # DAQ setup
        #UL.cbDConfigPort(self.boardNum, UL.FIRSTPORTA, UL.DIGITALOUT)
        #UL.cbDConfigPort(self.boardNum, UL.FIRSTPORTB, UL.DIGITALOUT)

        UL.d_config_port(self.boardNum,
                         DigitalPortType.FIRSTPORTA,
                         DigitalIODirection.OUT)

        UL.d_config_port(self.boardNum,
                         DigitalPortType.FIRSTPORTB,
                         DigitalIODirection.OUT)

        self.needToSendStimcode = False

        # CSV logging setup
        self.timer = core.Clock()
        self.triggerTimes = []
        self.stimCodes = []
        self.dateTime = datetime.datetime.now()

    # standard pre / post functions
    def preStim(self, args):
        stimNumber = args

        # record the stim number we're about to display
        self.stimCodes.append(stimNumber)

        # send stimcode to CED via measurement computing
        #UL.cbDOut(self.boardNum, UL.FIRSTPORTA, stimNumber)
        #UL.cbDOut(self.boardNum, UL.FIRSTPORTB, self.basestate)

        UL.d_out(self.boardNum,
                 DigitalPortType.FIRSTPORTA,
                 stimNumber)

        UL.d_out(self.boardNum,
                 DigitalPortType.FIRSTPORTB,
                 self.basestate)

        # wait for 2pt frame trigger
        if self.readSer:
            self.waitForSerial()

        # Tell ourselves to send the signal the CED as soon as we flip
        self.needToSendStimcode = True

    def postStim(self, args):
        pass

    def preFlip(self, args):
        # UL.cbDOut(self.boardNum, UL.FIRSTPORTB, self.basestate)  # return to base state
        UL.d_out(self.boardNum,
                 DigitalPortType.FIRSTPORTB,
                 self.basestate)

    def postFlip(self, args):
        if self.needToSendStimcode:
            # record the time at the first flip
            self.triggerTimes.append(self.timer.getTime())
            # Tell CED to read stimcode
            # this costs 1.2ms (+/- 0.1ms).
            #UL.cbDOut(self.boardNum, UL.FIRSTPORTB, (self.basestate+1) % 2)

            UL.d_out(self.boardNum,
                     DigitalPortType.FIRSTPORTB,
                     (self.basestate+1) % 2)

            # Only need to do this once per stim
            self.needToSendStimcode = False
        # UL.cbDOut(self.boardNum, UL.FIRSTPORTB, self.basestate+2)  # this should be an every frame trigger
        UL.d_out(self.boardNum,
                 DigitalPortType.FIRSTPORTB,
                 self.basestate+2)

    def wrapUp(self, logFilePath, expName):
        with open(logFilePath, "a") as csvfile:
            w = csv.writer(csvfile, dialect="excel")
            w.writerow(["==========="])
            w.writerow([expName])
            w.writerow([self.dateTime])
            w.writerow([logFilePath])
            w.writerow([self.stimCodes])
            w.writerow([self.triggerTimes])
            w.writerow(["Finished at ", datetime.datetime.now()])

    # additional functions
    def waitForSerial(self):
        # wait for the next time a trigger appears on the serial port
        # Make sure
        #  to call ser.flushInput() so that the buffer will be clear before we reach here.
        bytes = b''
        self.ser.flushInput()
        while bytes == b'':
            self.ser.flushInput()
            bytes = self.ser.read()
            

    def waitForXTriggers(self, trigToWait):
        self.waitForSerial()
        for count in range(0, trigToWait-1):
            time.sleep(0.015)
            self.waitForSerial()

    def getTimeBetweenTriggers(self):
        print("Waiting for serial trigger on ", self.serialPortName, ".")
        timer = core.Clock()
        offTime = None
        self.waitForSerial()
        onTime = timer.getTime()
        for count in range(0, 10):
            # Wait 15 msecs - this is because the serial triggers stay on for 10ms each,
            # and we don't want to count a single trigger multiple times
            time.sleep(0.015)
            self.waitForSerial()
        offTime = timer.getTime()
        frameTime = (offTime-onTime)/10
        print("frame triggers are ", frameTime, " seconds apart.")
        return frameTime

    def extendStimDurationToFrameEnd(self, stimDuration):
        if self.readSer:
            # find how often we receive triggers
            frameTime = self.getTimeBetweenTriggers()
            # adjust stim duration to be some multiple of the frame time
            stimDurationInFrames = math.ceil(stimDuration / frameTime)
            error1 = abs(stimDuration-(frameTime * stimDurationInFrames))
            error2 = abs(stimDuration-(frameTime * stimDurationInFrames-1))
            if error2 <= error1:
                stimDurationInFrames = stimDurationInFrames-1
            stimDuration = frameTime * stimDurationInFrames
            print("stim duration has been adjusted to ", stimDuration, " seconds (", stimDurationInFrames, " frames).")
        return stimDuration

    def preTrialLogging(self, *args):
        dataDirName = args[0]
        animalName = args[1]
        expName = args[2]
        stimCodeName = args[3]
        orientations = args[4]
        logFilePath = args[5]
        datapath = dataDirName+animalName+'\\'
        # write the dirname and expname for spike2
        f = open(dataDirName+'experimentname.txt', 'w')
        f.write(animalName)
        f.close()
        f = open(dataDirName+'instruction.txt', 'w')
        f.write(expName)
        f.close()
        # write the reference file, vht style
        destname = dataDirName+animalName+'\\'+expName+'\\'
        if not path.exists(destname):
            makedirs(destname)
        f = open(destname+'reference.txt', 'w')
        f.write('name\tref\ttype\ntp\t'+str(1)+'\tprairietp')
        f.close()
        # now write the stim parameters
        stimCodeName = stimCodeName.replace('.pyc', '.py')
        shutil.copy(stimCodeName, destname)
        trigcodename = path.dirname(path.realpath(__file__))+'\\'+path.basename(__file__)
        # if trigger was already compiled, __file__ is the pyc, not the human readable py.
        trigcodename = trigcodename.replace('.pyc', '.py')
        shutil.copy(trigcodename, destname)
        # explicitly write orientations
        oout = str(orientations)
        oout = oout.replace('[', '')
        oout = oout.replace(']', '')
        f = open(destname+'stimorientations.txt', 'w')
        f.write(oout)
        f.close()
        with open(logFilePath, "a") as csvfile:
            w = csv.writer(csvfile, dialect="excel")
            w.writerow(["==========="])
            w.writerow([animalName, " ", expName, " Started at ", datetime.datetime.now()])

    def getNextExpName(self, *args):
        dataDirName = args[0]
        animalName = args[1]
        currentDirs = [x.name for x in Path(dataDirName).joinpath(animalName).glob('t*') if x.is_dir()]
        
        currentDir = natsort.natsorted(currentDirs)[-1]
        expNum = int(re.compile('\d+$').search(currentDir)[0])
        expName = f't{str(expNum+1).zfill(5)}'
        return expName

    def logToFile(self, filename, data):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            f.write(data)
