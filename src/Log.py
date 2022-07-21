import logging
import os


class Log:
    @staticmethod
    def get_logger(path='./logs/', file_name = 'ChessEngine.log', save_to_file = True):
        log_format = '%(levelname)s: %(filename)s: %(message)s'
        if save_to_file:
            if not os.path.exists(path):
                os.makedirs(path)
            path_to_file = os.path.join(path,file_name)
            logging.basicConfig(filename=path_to_file,
                                format=log_format)
        else:
            logging.basicConfig(format=log_format)
        logger = logging.getLogger('log')
        logger.setLevel(1)
        return logger
