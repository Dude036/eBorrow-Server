#!/usr/bin/python3

from multiprocessing import Process, SimpleQueue
from database import auto_backup
from errors import error_handler
from networking import network_main
from decoder import decoding
from logger import STOP
import logging
import time

decode_buffer = SimpleQueue()
transmit_buffer = SimpleQueue()
error_buffer = SimpleQueue()


if __name__ == '__main__':
    print("Starting Server")
    # Set three infinite running tasks.
    # 1) Listen on the network for data
    # 2) Listen on the Decoding Queue to interpret data
    # 3) Listen on the Error Queue to send return messages
    # 4) Scheduled backups
    runnables = [
        Process(target=network_main, args=tuple((decode_buffer, error_buffer))),
        Process(target=decoding, args=tuple((decode_buffer, error_buffer, transmit_buffer))),
        Process(target=error_handler, args=iter((error_buffer, transmit_buffer))),
        Process(target=auto_backup)]
    # Run the tasks
    for r in runnables:
        logging.info("Beginning: %s" % str(r))
        r.start()

    while not STOP():
        time.sleep(30)

    # End the tasks. Since the above is infinite, this will never reach unless all thread have an unexpected error
    for r in runnables:
        r.terminate()
        logging.info("Ended: %s" % str(r))

    print("Ending Server")
