import logging
import simplejson as json

open('out.log', 'w')
logging.basicConfig(format='%(asctime)s :: %(levelname)8s :: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', filename='out.log', level=logging.DEBUG)


def STOP():
    """
    A Function to determine if we need to stop the server
    :return: True - If it needs to stop
            False - continue operation
    """
    return False if json.load(open('config.json'))['run'] == 1 else True
