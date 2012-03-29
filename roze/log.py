import logging

formatter = logging.Formatter(
    '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')

consoleLogger = logging.StreamHandler()
consoleLogger.setLevel(logging.INFO)
consoleLogger.setFormatter(formatter)
logging.getLogger('').addHandler(consoleLogger)

fileLogger = logging.FileHandler(filename='logs/debug.log')
#fileLogger.setLevel(logging.ERROR)
fileLogger.setFormatter(formatter)
logging.getLogger('').addHandler(fileLogger)

logger = logging.getLogger('Box')
logger.setLevel(logging.INFO)