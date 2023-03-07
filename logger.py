import logging


class Logger:
    def __init__(self):
        logging.basicConfig(filename="log.txt", level=logging.DEBUG,
                            format="%(asctime)s %(message)s", filemode="w")
        logging.debug("Logger is starting..");

    @staticmethod
    def add_log(level, message):
        if level == "debug":
            logging.debug(message)
        if level == "info":
            logging.info(message)
        if level == "warning":
            logging.warning(message)
        if level == "error":
            logging.error(message)
        if level == "critical":
            logging.critical(message)