import logging
import datetime


class Logger:
    def __init__(self, logger_name, filename):
        # Get the current date and time
        current_datetime = datetime.datetime.now()
        date = current_datetime.date()
        time = current_datetime.strftime("%H:%M:%S")

        self.log = logging.getLogger(logger_name)
        handler = logging.FileHandler(f'/home/karolisr/PycharmProjects/10by10game_RL/src/logs/{date}_{time}_{filename}')
        formatter = logging.Formatter("%(message)s")

        self.log.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def write(self, message):
        self.log.info(message)
