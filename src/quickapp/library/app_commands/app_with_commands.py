from abc import abstractmethod, ABCMeta
from psutil._compat import defaultdict
from quickapp.library.app.quickapp_imp import QuickApp
from quickapp.utils.script_utils import UserError
import logging
from quickapp.library.app.quickapp_interface import QuickAppBase
from quickapp import logger

class QuickMultiCmd(QuickApp):
    
    def get_parent(self):
        """ Returns the QuickMultiCmdApp parent """
        return self.parent
    

class QuickMultiCmdApp(QuickAppBase):
    __metaclass__ = ABCMeta
 
    def __init__(self, logger=None):
        QuickAppBase.__init__(self)
    
    def define_program_options(self, params):
        self.define_multicmd_options(params)
        params.accept_extra()
        
    @abstractmethod
    def define_multicmd_options(self, params):
        pass
    
    @abstractmethod
    def initial_setup(self):
        pass

    def get_usage(self):
        return 'prog [general options] <command> [command options]'
    
    def go(self):
#         prog = self.get_prog_name()
                
        # TODO: FIXME
        # print '%(prog) [general options] <command> [command options]'
#         description = self.get_program_description()
#         epilog = self._get_epilog()
#            
#         parser = argparse.ArgumentParser(prog=prog, usage=usage, description=description,
#                                          epilog=epilog)
#         app_params.populate_parser(parser)
#         values, given, extra = app_params.parse_using_parser_extra(parser, args)
#         options = DecentParamsResults(values, given, app_params.params)
#         self._options = options
#         

        self.initial_setup()
        
        cmds = self._get_subs_as_dict()
        if not cmds:
            msg = 'No commands defined.'
            raise ValueError(msg) 

        extra = self.get_options().get_extra()        
        if not extra:
            msg = 'Please specify as a command one of %s.' % self._get_subs_names_fmt()
            raise UserError(msg)  # XXX: use better exception
        
        cmd_name = extra[0]
        cmd_args = extra[1:]
        if not cmd_name in cmds:
            msg = ('Could not find command %s; please use one of %s.' % 
                   (cmd_name, self._get_subs_names_fmt()))
            raise UserError(msg)
        
        sub = cmds[cmd_name]
        
        sub_inst = sub()
        assert isinstance(sub_inst, QuickMultiCmd)
        logger_name = '%s-%s' % (self.get_prog_name(), cmd_name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        sub_inst.logger = logger
        # sub_inst.parent = self
        
        sub_inst.main(args=cmd_args, parent=self)
        
    
    def get_epilog(self):
        subs = self._get_subs()
        if not subs:
            return 'Warning: no commands defined.'
            
        s = "Commands: \n"        
        for sub in self._get_subs():
            cmd_name = sub.cmd
            cmd_short = sub.__dict__.get('short', 'No description available')
            s += "  %30s  %s\n" % (cmd_name, cmd_short)
             
        return s
        # print 'subcommands: ', self.get_subs().keys()
    
    def _get_subs_names_fmt(self):
        """ Returns 'cmd1, cmd2, cmd3; """
        names = self._get_subs_names()
        possibilities = ', '.join('%r' % x for x in names)
        return possibilities
        
    def _get_subs_as_dict(self):
        """ Returns a dict: cmd_name -> cmd """
        return dict([(x.cmd, x) for x in self._get_subs()])

    def _get_subs_names(self):
        return [x.cmd for x in self._get_subs()]
    
    def _get_subs(self):
        this_class = type(self)
        return QuickMultiCmdApp.subs[this_class]
        
    # QuickMultiCmdApp subclass -> (string -> QuickApp) 
    subs = defaultdict(list)
        

def add_subcommand(app, cmd):
    logger.info('Adding command  %s - %s' % (app.cmd, cmd.cmd))
    # cmd_name = cmd.cmd
    cmds = QuickMultiCmdApp.subs[app]
#     if cmd_name in cmds:
#         msg = 'Duplicate sub command %r.' % cmd_name
#         raise ValueError(msg) 
#     cmds[cmd_name] = cmd
    cmds.append(cmd)


