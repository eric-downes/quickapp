from .. import Choice, comp_comb
from abc import abstractmethod, ABCMeta
from compmake import comp

class QuickAppInterface(object):
    __metaclass__ = ABCMeta

    # Interface to be implemented
    
    @abstractmethod
    def define_options(self, params):
        """ Must be implemented """
        pass

    @abstractmethod
    def define_jobs(self):
        pass

    # Resources
    def get_options(self):
        return self._options

    def get_output_dir(self):
        """ Returns a suitable output directory for data files """
        return self._output_dir

    def add_report(self, report, report_type=None):
        rm = self.get_report_manager()
        rm.add(report, report_type, **self._current_params)

    def get_report_manager(self):
        return self._report_manager
    
    # Other utility stuff
    
    @staticmethod
    def choice(it):
        return Choice(it)
    
    def comp_comb(self, *args, **kwargs):
        return comp_comb(*args, **kwargs)
    
    def comp(self, *args, **kwargs):
        """ Simple wrapper for Compmake's comp function. """
        return comp(*args, **kwargs)
