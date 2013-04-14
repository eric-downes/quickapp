from abc import abstractmethod, ABCMeta
from quickapp.library.params.decent_params import DecentParams
from quickapp.utils.has_logger import HasLogger
import logging
from conf_tools.utils.indent_string import indent
import traceback
from quickapp.utils.script_utils import UserError
from contracts import contract
from contracts.interface import describe_value


class QuickAppBase(HasLogger):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None):
        HasLogger.__init__(self)
        self.parent = parent
        
        logger_name = self.get_prog_name()
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        self.logger = logger
    
    @abstractmethod
    def define_program_options(self, params):
        """ Must be implemented """
        pass

    @abstractmethod
    @contract(returns='None|int')
    def go(self):
        """ Must be implemented. Should return either None => success, or an integer error code. """
        pass
    
    def get_program_description(self):
        pass
    
    def get_usage(self):
        pass
    
    def get_epilog(self):
        pass
    
    def get_options(self):
        return self._options

    def get_parent(self):
        return self.parent
        
    def get_prog_name(self):
        klass = type(self)
        if not 'cmd' in klass.__dict__:
            msg = 'Please specify "cmd" in class %s.' % klass
            raise ValueError(msg)
        return klass.__dict__['cmd']
    
    @contract(args='None|list(str)', returns=int)
    def main(self, args=None, parent=None):
        """ Returns an integer """ 
        # Create the parameters and set them using args
        self.parent = parent
        self.set_options_from_args(args)
        ret = self.go()
        if ret is None:
            ret = 0
        
        if isinstance(ret, int):
            return ret
        else:
            msg = 'Expected None or an integer fomr self.go(), got %s' % describe_value(ret)
            raise ValueError(msg)
        

    def set_options_from_args(self, args):
        """
        
            raises: UserError: Wrong configuration, user's mistake.
                    Exception: all other exceptions
        """
        prog = self.get_prog_name()
        params = DecentParams()
        self.define_program_options(params)
        
        try:
            self._options = params.get_dpr_from_args(prog=prog, args=args,
                                                     usage=self.get_usage(),
                                                     description=self.get_program_description(),
                                                     epilog=self.get_epilog())
        except UserError:
            raise
        except Exception as e:
            msg = 'Could not interpret:\n'
            msg += ' args = %s\n' % args
            msg += 'according to params spec:\n'
            msg += indent(str(params), '| ') + '\n'
            msg += 'Error is:\n'
            msg += indent(traceback.format_exc(e), '> ')
            raise Exception(msg)  # XXX class
        
 
