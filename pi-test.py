import os
import os.path
import re
import sys
import logging
import time
import RPi.GPIO as GPIO
from subprocess import Popen
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("Rotating Log")

#------------ CREATE LOG ROTATION CONFIG -----------------------
def create_rotating_log(path):
    """
    Creates a rotating log
    """

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logger.setLevel(logging.DEBUG)

    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=1000*1024, backupCount=10, mode='a') # let max size be 1 Mb
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
    logger.addHandler(handler)

create_rotating_log("logs/pi-test.log")

R = re.compile("\d+")

pin_info = {}

def read_base_path_config(file_name) :
    try:
        logger.debug("Opening configuration file [%s] ..." % file_name)
        return open(file_name.rstrip()).read()
    except:
        logger.error("Failed to read config file %s [ due to: %s" % (file_name, sys.exc_info()[0]))
        print("Error while reading config file: %s" % sys.exc_info()[0])
        sys.exit(-1)

# read from configuration file a base_path with videos linked to pins
BASE_PATH = read_base_path_config("./config").strip()

def show_pins() :
    """
    List all subfolders which matchind pin configuration
    :return: list of subfolder with numeric name only
    """
    return [folder for folder in os.listdir(BASE_PATH) if R.match(folder)]

def play_video(pin) :
    Popen(['omxplayer', '-b', video_path(pin)])

def video_path(pin) :
    path = "%s/%s/" % (BASE_PATH, pin)
    first_file = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
    return first_file

def loop() :
    while True:
        print("Running main loop")
        logger.debug("Running main loop")
        time.sleep(0.2)
        for pin in pin_info.values() :
            readVal = GPIO.input(pin)
            print("state of pin[%s] is %s" % (pin, readVal))
            if readVal == 0 :
                play_video(pin)

def main() :
    """
    Main service entry-point.
    performs all intialializations and running main loop
    :return: nothing
    """
    logger.info("starting pi-test....")
    print("starting pi-test....")
    for p in show_pins() :
        pin_info.update({"%s" % p :  int(p)})
    logger.info("pins are configured: %s" % pin_info.values())
    print("pins are configured: %s" % pin_info.values())
    print(("Starting service in loop..."))
    GPIO.setmode(GPIO.BCM)
    for p in pin_info.values() :
        logger.debug("Initializing pin [%s,\tIN,\tGPIO_PUD_UP,\tvideo=%s]" % (p, video_path(p) ))
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    loop()

main()

