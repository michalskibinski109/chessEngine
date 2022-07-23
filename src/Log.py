import logging
import os
import sys


class Log:
    @staticmethod
    def get_logger(path='./logs/', file_name = 'ChessEngine.log', save_to_file = True):
        formatter = logging.Formatter('%(levelname)s: %(filename)s: %(message)s')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
        if save_to_file:
            if not os.path.exists(path):
                os.makedirs(path)
        file_handler = logging.FileHandler(os.path.join(path,file_name))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger
