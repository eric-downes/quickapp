from abc import abstractmethod, ABCMeta
from compmake import (batch_command, compmake_console, read_rc_files,
    use_filesystem)
from compmake.ui.ui import comp_prefix, get_comp_prefix
from conf_tools.utils import indent
from contracts import contract
from quickapp import logger, QUICKAPP_COMPUTATION_ERROR
from quickapp.library.app.quickapp_interface import QuickAppBase
from quickapp.utils import wrap_script_entry_point, UserError
from reprep.report_utils import ReportManager
import contracts
import os
import sys
import traceback
import warnings
from quickapp.library.context.resource_manager import ResourceManager
from quickapp.library.context.compmake_context import CompmakeContext


   

class QuickApp(QuickAppBase):

    __metaclass__ = ABCMeta

    # Interface to be implemented
    @abstractmethod
    def define_jobs_context(self, context):
        pass

    @abstractmethod
    def define_options(self, params):
        pass
             
    def _define_options_compmake(self, params):
        script_name = self.get_prog_name()
        default_output_dir = 'out-%s/' % script_name

        params.add_flag('contracts', help='Activate PyContracts')
        params.add_flag('profile', help='Use Python Profiler')
        params.add_string('output', short='o', help='Output directory',
                               default=default_output_dir)
    
        params.add_flag('console', help='Use Compmake console')

        params.add_string('command', short='c',
                      help="Command to pass to compmake for batch mode",
                      default='make')
    
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
        
        if not options['contracts']:
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
        resource_manager = ResourceManager(None)
        
        job_prefix = None
        context = CompmakeContext(parent=None, qapp=self, job_prefix=job_prefix,
                                  report_manager=report_manager,
                                  resource_manager=resource_manager,
                                  output_dir=outdir)
        resource_manager.context = context  #  XXX not elegant
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
                print('batch_command returned %s' % batch_result)
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
                       add_job_prefix=None):     
        instance = cmd_class()
        instance.parent = self
        is_quickapp = isinstance(instance, QuickApp) 
        
        try:

            # we are already in a context; just define jobs
            child_context = context.child(qapp=self, name=child_name, extra_dep=extra_dep,
                                          add_outdir=add_outdir, add_job_prefix=add_job_prefix)  # XXX
        
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
                res = instance.define_jobs_context(child_context)
                
            # Add his jobs to our list of jobs
            context._jobs.update(child_context.all_jobs_dict()) 
            return res
        
        except Exception as e:
            msg = 'Error while trying to call recursive:\n'
            msg += ' class = %s\n' % cmd_class
            msg += ' args = %s\n' % args
            if '_options' in instance.__dict__:
                msg += ' parsed options: %s\n' % instance.get_options()
                msg += ' params: %s\n' % instance.get_options().get_params()
            msg += indent(traceback.format_exc(e), '> ')
            raise Exception(msg)
      

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
                            exceptions_no_traceback=(UserError,),
                            args=args, sys_exit=sys_exit)


  
#         
# # TODO: remove
# def create_conf_name_digest(values, length=12):
#     """ Create an hash for the given values """
#     s = "-".join([str(values[x]) for x in sorted(values.keys())])
#     h = hashlib.sha224(s).hexdigest()
#     if len(h) > length:
#         h = h[:length]
#     return h


# run_name = create_conf_name_digest(options, length=12)
# self.logger.info('Configuration name: %r' % run_name)
# (end)
#         run_name = 'no-conf'
# outdir = os.path.join(options.output, run_name)

#
# def create_conf_name(values, given, limit=32):
#    cn = create_conf_name_values(values, given)
#    if len(cn) > limit:
#        cn = cn[:limit]  # TODO XXX
#    return cn
#    
    
#    
# def create_conf_name_values(values, given):
#    def make_short(a):
#        if isinstance(a, Choice):
#            s = ','.join([make_short(x) for x in a])
#        else:
#            s = str(a)
#        if '/' in s:
#            s = os.path.basename(s)
#            s = os.path.splitext(s)[0]
#            s = s.replace('.', '_')
#        s = s.replace(',', '_')
#        return s
#    return "-".join([make_short(values[x]) for x in sorted(given)])
#    
#    
    

         
        
#     def old_stuff():
#         combs = {}
#         for params, choices in all_combinations(options, give_choices=True):
#             i = len(combs)
#             name = 'C%03d' % i
#             warnings.warn('xx')
#             combs[name] = dict(params=params, choices=choices, given=options.get_given())
#                      
#         app_params = None; 
#         self.add_combs(outdir, combs, app_params)        
# 
#         def add_combs(self, outdir, combs, app_params):
#             multiple = len(combs) > 1
#             for name, x in combs.items():
#                 params = x['params']
#                 choices = x['choices']
#                 given = x['given']
#                 if multiple:
#                     self.logger.info('Config %s: %s' % (name, choices))
#                     comp_prefix(name) 
#                 self._options = DecentParamsResults(params, given, app_params.params)
#                 self._current_params = params
#                 
#                 self._output_dir = os.path.join(outdir, 'output', name)
#     
#                 self.define_jobs()
#                 # TODO: check that we defined some jobs
#                 
#             if multiple:
#                 comp_prefix()
#     
#     @staticmethod
#     def choice(it):
#         return Choice(it)
#     # Other utility stuff
#     
#     @staticmethod
#     def choice(it):
#         return Choice(it)
#     
#     def comp_comb(self, *args, **kwargs):
#         return comp_comb(*args, **kwargs)

# new_contract('QuickApp', QuickApp)
# new_contract('CompmakeContext', CompmakeContext)
 
 
 
