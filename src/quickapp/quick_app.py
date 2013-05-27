from .compmake_context import CompmakeContext
from .quick_app_base import QuickAppBase
from .report_manager import ReportManager
from abc import abstractmethod
from compmake import (batch_command, compmake_console, read_rc_files,
    use_filesystem, comp_prefix, get_comp_prefix)
from conf_tools.utils import indent
from contracts import contract
from decent_params.utils import wrap_script_entry_point, UserError
from quickapp import logger, QUICKAPP_COMPUTATION_ERROR
import contracts
import os
import sys
import traceback
import warnings
from contracts.metaclass import ContractsMeta
from quickapp.exceptions import QuickAppException


__all__ = ['QuickApp', 'quickapp_main']


class QuickApp(QuickAppBase):

    """ Template for an application that uses compmake to define jobs. """

    __metaclass__ = ContractsMeta


    # Interface to be implemented
    @abstractmethod
    def define_jobs_context(self, context):
        """ Define jobs in the current context. """
        pass

    @abstractmethod
    def define_options(self, params):
        """ Define options for the application. """
        pass
             
    def _define_options_compmake(self, params):
        script_name = self.get_prog_name()
        default_output_dir = 'out-%s/' % script_name

        g = 'Generic arguments for Quickapp'
        # TODO: use  add_help=False to ARgParsre
        # params.add_flag('help', short='-h', help='Shows help message')
        params.add_flag('contracts', help='Activate PyContracts', group=g)
        params.add_flag('profile', help='Use Python Profiler', group=g)
        params.add_string('output', short='o',
                          help='Output directory',
                                    default=default_output_dir, group=g)
    
        params.add_flag('console', help='Use Compmake console', group=g)

        params.add_string('command', short='c',
                      help="Command to pass to compmake for batch mode",
                      default='make', group=g)
    
    def define_program_options(self, params):
        self._define_options_compmake(params)
        self.define_options(params)
    
    
    def get_qapp_parent(self):
        parent = self.parent
        while parent is not None:
            # logger.info('Checking %s' % parent)
            if isinstance(parent, QuickApp):
                return parent
            parent = parent.parent
        return None
        
    def go(self):  
        # check that if we have a parent who is a quickapp,
        # then use its context      
        qapp_parent = self.get_qapp_parent()
        if qapp_parent is not None:
            # self.info('Found parent: %s' % qapp_parent)
            context = qapp_parent.child_context  
            self.define_jobs_context(context)
            return
        else:
            # self.info('Parent not found')
            pass
            
        options = self.get_options()
        
        if self.get_qapp_parent() is None:
            # only do this if somebody didn't do it before
            if not options.contracts:
                msg = 'PyContracts disabled for speed. Use --contracts to activate.'
                self.logger.warning(msg)
                contracts.disable_all()

        warnings.warn('removed configuration below')  # (start)

        outdir = options.output
        
        # Compmake storage for results        
        storage = os.path.join(outdir, 'compmake')
        use_filesystem(storage)
        read_rc_files()
        
        
        # Report manager
        reports = os.path.join(outdir, 'reports')
        reports_index = os.path.join(outdir, 'reports.html')
        report_manager = ReportManager(reports, reports_index)
        
        job_prefix = None
        context = CompmakeContext(parent=None, qapp=self, job_prefix=job_prefix,
                                  report_manager=report_manager,
                                  output_dir=outdir)
        self.context = context
        original = get_comp_prefix()
        self.define_jobs_context(context)
        comp_prefix(original) 
        
        self.context.get_report_manager().create_index_job()
        
        if context.n_comp_invocations == 0:
            # self.comp was never called
            msg = 'No jobs defined.'
            raise ValueError(msg)
        else: 
            if not options.console:
                batch_result = batch_command(options.command)
                if isinstance(batch_result, str):
                    ret = QUICKAPP_COMPUTATION_ERROR
                elif isinstance(batch_result, int):
                    if batch_result == 0:
                        ret = 0
                    else:
                        # xxx: discarded information
                        ret = QUICKAPP_COMPUTATION_ERROR
                else:
                    assert False 
                return ret
            else:
                compmake_console()
                return 0

    @contract(args='dict(str:*)|list(str)', extra_dep='list')
    def call_recursive(self, context, child_name, cmd_class, args,
                       extra_dep=[],
                       add_outdir=None,
                       add_job_prefix=None,
                       separate_resource_manager=False):     
        instance = cmd_class()
        instance.set_parent(self)
        is_quickapp = isinstance(instance, QuickApp) 
        # print('%s->%s %s' % (self, cmd_class, separate_resource_manager))
        try:
            # we are already in a context; just define jobs
            child_context = context.child(qapp=instance, name=child_name,
                                          extra_dep=extra_dep,
                                          add_outdir=add_outdir,
                                          separate_resource_manager=separate_resource_manager,
                                          add_job_prefix=add_job_prefix)  # XXX
        
            if isinstance(args, list):
                instance.set_options_from_args(args)
            elif isinstance(args, dict):
                instance.set_options_from_dict(args)
            else:
                assert False
            
            if not is_quickapp:
                # self.info('Instance is not quickapp! %s' % type(instance))
                self.child_context = child_context
                res = instance.go()  
            else:
                instance.context = child_context
                res = instance.define_jobs_context(child_context)
                
            # Add his jobs to our list of jobs
            context._jobs.update(child_context.all_jobs_dict()) 
            return res
        
        except Exception as e:
            msg = 'While trying to run  %s\n' % cmd_class.__name__
            msg += 'with arguments = %s\n' % args
            if '_options' in instance.__dict__:
                msg += ' parsed options: %s\n' % instance.get_options()
                msg += ' params: %s\n' % instance.get_options().get_params()
            if isinstance(e, QuickAppException):
                msg += indent(str(e), '> ')
            else:
                msg += indent(traceback.format_exc(e), '> ')
            raise QuickAppException(msg)
      

def quickapp_main(quickapp_class, args=None, sys_exit=True):
    """
        Use like this:
        
            if __name__ == '__main__':
                quickapp_main(MyQuickApp)
                
        
        if sys_exit is True, we call sys.exis(ret), otherwise we return the value.
         
    """
    instance = quickapp_class()
    if args is None:
        args = sys.argv[1:]
        
    return wrap_script_entry_point(instance.main, logger,
                            exceptions_no_traceback=(UserError, QuickAppException),
                            args=args, sys_exit=sys_exit)


