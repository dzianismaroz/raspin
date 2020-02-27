import os
import re
import sys
import logging
import time
#import RPi.GPIO as GPIO

logging.basicConfig( filename='pi-test.log' \
                    , filemode='w' \
                    , level=logging.DEBUG \
                    , format='%(asctime)s %(message)s' \
                    , datefmt='%m-%d-%Y %H:%M:%S' )

R = re.compile("\d+")

pin_info = {}

def read_base_path_config(file_name) :
    try:
        logging.debug(f'Opening configuration file [{file_name}]...')
        return open(file_name).read()
    except:
        logging.error(f'Failed to read config file [{file_name}] due to: {sys.exc_info()[0]}')
        print(f'Error while reading config file: {sys.exc_info()[0]}')
        sys.exit(-1)

# read from configuration file a base_path with videos linked to pins
BASE_PATH = read_base_path_config("./config")

def show_pins() :
    """
    List all subfolders which matchind pin configuration
    :return: list of subfolder with numeric name only
    """
    return [folder for folder in os.listdir(BASE_PATH) if R.match(folder)]


def loop() :
    while True:
        print(f'Running main loop')
        logging.debug(f'Running main loop')
        time.sleep(0.2)

def main() :
    """
    Main service entry-point.
    performs all intialializations and running main loop
    :return: nothing
    """
    logging.info("starting pi-test....")
    print("starting pi-test....")
    for p in show_pins() :
        pin_info.update({f'{p}' :  int(p)})
    logging.info(f'pins are configured: {pin_info.values()}');
    print(f'pins are configured: {pin_info.values()}')
    print(("Starting service in loop..."))
    #GPIO.setmode(GPIO.BCM)
    for p in pin_info.values() :
        logging.debug(f'Initializing pin [{p},\tIN,\tGPIO_PUD_UP]')
        #GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    loop()

main()

