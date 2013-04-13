import logging

class HasLogger(object):
    
    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
        self.logger = logger
        
    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)
    
    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)
