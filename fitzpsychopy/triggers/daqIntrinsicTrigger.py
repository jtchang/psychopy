# Daq Triggering - triggers when stimcodes arrive via a Measurement Computing DAQ
# used in intrinsic imaging experiments in the SLM room
import mcculw.ul as UL
from mcculw.enums import DigitalIODirection, DigitalPortType
from .abstractTrigger import trigger
from os import path,makedirs
import shutil
import glob
import  csv, datetime
from pathlib import Path


class daqIntrinsicTrigger(trigger):
    def __init__(self, *args):  
        #DAQ setup
        self.boardNum = 0
        #UL.cbDConfigPort(self.boardNum,UL.FIRSTPORTA, UL.DIGITALIN)

        UL.d_config_port(self.boardNum,
                         DigitalPortType.FIRSTPORTA,
                         DigitalIODirection.IN
                         )

    def preStim(self, args):
        print('Waiting for stimcode to arrive on DAQ...')
        stimcode = 0
        while stimcode > 64 or stimcode == 0:
            #keep trying until a valid stimcode appears
            #stimcode = UL.cbDIn(self.boardNum, UL.FIRSTPORTA, stimcode)
            
            stimcode = UL.d_in(self.boardNum,
                               DigitalPortType.FIRSTPORTA,
                               stimcode)
            
            
        print(f'Got stimcode {stimcode}')
        return stimcode-1

    def preTrialLogging(self, *args):
        dataDirName = args[0]
        animalName = args[1]
        expName = args[2]
        stimCodeName = args[3]
        orientations = args[4]
        logFilePath = args [5]
      
        expt_name_txt = Path(dataDirName).joinpath('experimentname.txt')
        instruction_name_txt = Path(dataDirName).joinpath('instruction.txt')
        
        # write the dirname and expname for spike2
        
        with open(str(expt_name_txt), 'w') as f:
            f.write(animalName)
        
        with open(str(instruction_name_txt), 'w') as f:
            f.write(expName)
        # write the reference file, vht style
        
        dest_path = Path(dataDirName).joinpath(animalName,expName)
        dest_path.mkdir(parents=True, exist_ok=False)

        with open(str(dest_path.joinpath('reference.txt')), 'w') as f:
            f.write(f'name\tref\ttype\ntp\t{str(1)}\tprairietp')
        
        
        # now write the stim parameters
        stimCodeName=stimCodeName.replace('.pyc','.py')
        shutil.copy(stimCodeName,str(dest_path))
        trigcodename=str(Path(path.dirname(path.realpath(__file__))).joinpath(path.basename(__file__)))
        trigcodename=trigcodename.replace('.pyc','.py') # if trigger was already compiled, __file__ is the pyc, not the human readable py.
        shutil.copy(trigcodename,destname)
        
        
        # explicitly write orientations
        oout = ','.join(map(str,orientations))
        
        
        with open(dest_path.joinpath('stimorientations.txt'), 'w') as f:
            f.write(oout)
        
        
        with open(logFilePath, 'a') as csvfile:
            w = csv.writer(csvfile, dialect = 'excel')
            w.writerow(['==========='])
            w.writerow([animalName,' ',expName,' Started at ',datetime.datetime.now()])
            
            
    def getNextExpName(self,args):
        dataDirName = args[0]
        animalName = args[1]
        currentDirs=glob.glob(f'{dataDirName}{animalName}\\t*')
        startInt=len(dataDirName)+len(animalName)+3
        mxdir=0
        for d in currentDirs:
            this=int(d[startInt:len(d)])
            mxdir=max(mxdir,this)
        expName=f't{mxdir+1:05.0f}'
        return expName
   
          
         
         