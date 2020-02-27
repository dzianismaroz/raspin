import os
import re
import sys
import logging

logging.basicConfig( filename='pi-test.log' \
                    , filemode='w' \
                    , level=logging.DEBUG \
                    , format='%(asctime)s %(message)s' \
                    , datefmt='%m-%d-%Y %I:%M:%S' )

R = re.compile("\d+")

def read_base_path_config(file_name) :
    try:
        return open(file_name).read()
    except:
        logging.error(f'Error while reading config file: {sys.exc_info()[0]}')
        print(f'Error while reading config file: {sys.exc_info()[0]}')

# read from configuration file a base_path with videos linked to pins
BASE_PATH = read_base_path_config("./config")

def show_pins() :
    """
    List all subfolders which matchind pin configuration
    :return: list of subfolder with numeric name only
    """
    return [folder for folder in os.listdir(BASE_PATH) if R.match(folder)]


def main() :
    """
    Main service entry-point.
    performs all intialializations and running main loop
    :return: nothing
    """
    logging.debug("starting pi-test....")
    print("starting pi-test....")
    logging.debug(f'pins are configured: {show_pins()}');
    print(f'pins are configured: {show_pins()}')

main()

