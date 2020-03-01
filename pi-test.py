import os
import os.path
import re
import sys
import logging
import time
import threading
import RPi.GPIO as GPIO
from subprocess import Popen
from logging.handlers import RotatingFileHandler

LOGGER = logging.getLogger("Rotating Log")


def create_rotating_log(path):
    """
    Creates a rotating log
    """

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    LOGGER.setLevel(logging.INFO)

    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=1000*1024, backupCount=10, mode='a') # let max size be 1 Mb
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%m-%d-%Y %H:%M:%S'))
    LOGGER.addHandler(handler)


create_rotating_log("logs/pi-test.log")

R = re.compile('\d+')

pin_info = {}
current_play = []


def log_exit():
    LOGGER.error("###### ERROR raspin service being terminated")
    sys.exit(-1)


def read_base_path_config(file_name):
    try:
        LOGGER.info("Opening configuration file [%s] ..." % file_name)
        return open(file_name.rstrip()).read()
    except Exception:
        LOGGER.error("##### ERROR Failed to read config file ./conf/%s [ due to: %s" % (file_name, sys.exc_info()[0]))
        log_exit()


# read from configuration file a base_path with videos linked to pins
BASE_PATH = read_base_path_config("conf/base_path").strip()


def show_pins():
    """
    List all subfolders which matchind pin configuration
    :return: list of subfolder with numeric name only
    """
    try:
        directories = os.listdir(BASE_PATH)
        return [f for f in directories if R.match(f)]
    except Exception:
        LOGGER.error("##### ERROR Failed to read pin directories path [%s] due to: %s" % (BASE_PATH, sys.exc_info()[0]))
        log_exit()


def extract_reset_pin():
    val = read_base_path_config('conf/reset').strip()
    for key in pin_info.keys():
        if val == key:
            del pin_info[key]
    return val


def play_video(pin):
    stop_video()
    video = video_path(pin)
    try:
        current_play.append(1)
        Popen(['omxplayer', '-b', '-o', 'hdmi', video, ' > /dev/null']).wait()
        LOGGER.info("Pin %s triggered" % pin)
        LOGGER.info("starting playback y pin = %s -> video = %s" % (pin, video))
    except Exception:
        LOGGER.error("##### ERROR while playback of video due to : %s" % sys.exc_info()[0])
        pass
    loop_video()


def loop_video():
    stop_video()
    current_play[:]=[]
    try:
        Popen(['omxplayer', '-b', '-o', 'hdmi', '--loop', video_path('default'), ' > dev/null'])
    except Exception:
        LOGGER.error("##### ERROR video playback due to %s" % sys.exc_info()[0])
        pass


def stop_video():
    try:
        Popen(['killall', 'omxplayer.bin']).wait()
    except Exception:
        LOGGER.error("##### ERROR while interrupting video playback")
        pass


def video_path(pin):
    path = "%s/%s/" % (BASE_PATH, pin)
    try:
        return next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
    except Exception:
        LOGGER.error("##### ERROR loading any video file by path: %s" % path)
        pass
        return "/dev/null"


def is_pin_triggered(val):
    return val == 0


def loop():
    loop_video()
    while True:
        time.sleep(0.2)
        for pin in pin_info.values():
            read_val_pin = GPIO.input(pin)
            if is_pin_triggered(read_val_pin):
                play_video(pin)


def reset_monitor():
    reset_pin = int(extract_reset_pin())
    while True:
        time.sleep(0.2)
        read_val = GPIO.input(reset_pin)
        if is_pin_triggered(read_val) and current_play:
            loop_video()
            LOGGER.info("RESETTING ALL VIDEOS")


def main():
    """
    Main service entry-point.
    performs all intialializations and running main loop
    :return: nothing
    """
    LOGGER.info("\n#############################################")
    LOGGER.info("starting pi-test....")

    for p in show_pins():
        pin_info.update({"%s" % p :  int(p)})

    LOGGER.info("pins are configured: %s" % pin_info.values())
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(extract_reset_pin()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for p in pin_info.values():
        LOGGER.info("Initializing pin [%s,\tIN,\tGPIO_PUD_UP,\tvideo=%s]" % (p, video_path(p)))
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    threading.Thread(target=loop).start()
    threading.Thread(target=reset_monitor).start()


if __name__ == '__main__':
    main()

