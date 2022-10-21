from triggers import noTrigger, serialTriggerDaqOut
import logging
logger = logging.getLogger()

def create_trigger(trigger_type,data_path, animal_name, **kwargs):
    logger.debug(kwargs.get('serial_port_name', None))
        
    if trigger_type in ['SerialDaqOut', 'OutOnly']:
        logger.info('Using trigger type %s', trigger_type)
        
        trigger = serialTriggerDaqOut(data_path,
                                      animal_name, 
                                      board_num=kwargs.get('board_num', 0),
                                      serial_port_num=kwargs.get('serial_port_name', 'COM3'))

        if trigger_type == 'OutOnly':
            trigger.readSer = False
        
        return trigger

            
    
    logger.info('Using NoTrigger type')
    return noTrigger(data_path, animal_name)
    