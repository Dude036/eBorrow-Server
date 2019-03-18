#!/usr/bin/python3

import simplejson as json
from multiprocessing import Process
from database import auto_backup
from errors import error_handler
from networking import network_main
from decoder import decoding


if __name__ == '__main__':
    # Set three infinite running tasks.
    # 1) Listen on the network for data
    # 2) Listen on the Decoding Queue to interpret data
    # 3) Listen on the Error Queue to send return messages
    # 4) Scheduled backups
    runnables = [Process(target=network_main), Process(target=decoding), Process(
        target=error_handler), Process(target=auto_backup)]

    # Run the tasks
    for r in runnables:
        print("Beginning:", str(r))
        r.start()

    # End the tasks. Since the above is infinite, this will never reach unless all thread have an unexpected error
    for r in runnables:
        r.join()
        print("Ended:", str(r))
