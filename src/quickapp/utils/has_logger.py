import logging

class HasLogger(object):
    
    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
        self.logger = logger
        
    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)

    def warn(self, *args, **kwargs):
        return self.logger.warn(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.logger.error(*args, **kwargs)
    
    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)
