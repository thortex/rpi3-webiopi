import logging

LOG_FORMATTER = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")        
ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.WARN)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
ROOT_LOGGER.addHandler(CONSOLE_HANDLER)

LOGGER = logging.getLogger("WebIOPi")

def setInfo():
    ROOT_LOGGER.setLevel(logging.INFO)

def setDebug():
    ROOT_LOGGER.setLevel(logging.DEBUG)
    
def debugEnabled():
    return ROOT_LOGGER.level == logging.DEBUG

def logToFile(filename):
    FILE_HANDLER = logging.FileHandler(filename)
    FILE_HANDLER.setFormatter(LOG_FORMATTER)
    ROOT_LOGGER.addHandler(FILE_HANDLER)

def debug(message):
    LOGGER.debug(message)

def info(message):
    LOGGER.info(message)

def warn(message):
    LOGGER.warn(message)

def error(message):
    LOGGER.error(message)

def exception(message):
    LOGGER.exception(message)

def printBytes(buff):
    for i in range(0, len(buff)):
        print("%03d: 0x%02X %03d %c" % (i, buff[i], buff[i], buff[i]))
        
