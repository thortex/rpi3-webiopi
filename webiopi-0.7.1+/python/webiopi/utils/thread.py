import time
import signal
import threading
from webiopi.utils import logger

RUNNING = False
TASKS = []

class Task(threading.Thread):
    def __init__(self, func, loop=False):
        threading.Thread.__init__(self)
        self.func = func
        self.loop = loop
        self.running = True
        self.start()
    
    def stop(self):
        self.running = False

    def run(self):
        if self.loop:
            while self.running == True:
                self.func()
        else:
            self.func()

def stop(signum=0, frame=None):
    global RUNNING
    if RUNNING:
        logger.info("Stopping...")
        RUNNING = False
        for task in TASKS:
            task.stop()
                

def runLoop(func=None, async=False):
    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    if func != None:
        if async:
            TASKS.append(Task(func, True))
        else:
            while RUNNING:
                func()
    else:
        while RUNNING:
            time.sleep(1)
