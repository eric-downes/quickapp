from abc import abstractmethod, ABCMeta
from quickapp.utils import UserError
import logging
from quickapp import QuickAppBase, QuickApp
from collections import defaultdict
from reprep.utils import deprecated


__all__ = ['QuickMultiCmdApp', 'add_subcommand']
 
 
# TODO: remove this class
class QuickMultiCmd(QuickApp):
    pass
     
    
class QuickMultiCmdAppMeta(ABCMeta):
    """ A way to create the accessory <cls>.sub 
        which is the subclass for commands. """
    def __init__(appcls, clsname, bases, clsdict):  # @UnusedVariable @NoSelf
        
        if clsname == 'QuickMultiCmdApp':
            return
        
        # print('Automatically triggered %s' % (appcls))
        
        class Register(ABCMeta):
            def __init__(cls, clsname, bases, clsdict):  # @UnusedVariable @NoSelf
                # print('Automatically registering %s>%s' % (cls, clsname))
                if clsname == 'SubCmd':
                    return
                cmds = QuickMultiCmdApp.subs[appcls]
                cmds.append(cls)

        class SubCmd(QuickAppBase):
            __metaclass__ = Register
            
            def get_parent(self):
                """ Returns the QuickMultiCmdApp parent """
                return self.parent
            
        appcls.sub = SubCmd
    
        # print 'Created ', appcls.sub
        
    
class QuickMultiCmdApp(QuickAppBase):
    __metaclass__ = QuickMultiCmdAppMeta
    
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
        names = self._get_subs_names()
        commands = ' | '.join(names)

        return '%prog ' + '[general options] {%s} [command options]' % commands
    
    def go(self):
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
        assert isinstance(sub_inst, QuickAppBase)
        logger_name = '%s-%s' % (self.get_prog_name(), cmd_name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        sub_inst.logger = logger
        
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
        
@deprecated
def add_subcommand(app, cmd):
    # logger.info('Adding command  %s - %s' % (app.cmd, cmd.cmd))
    # cmd_name = cmd.cmd
    cmds = QuickMultiCmdApp.subs[app]
    #     if cmd_name in cmds:
    #         msg = 'Duplicate sub command %r.' % cmd_name
    #         raise ValueError(msg) 
    #     cmds[cmd_name] = cmd
    cmds.append(cmd)


