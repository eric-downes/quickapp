from abc import abstractmethod, ABCMeta
from compmake import (batch_command, compmake_console, read_rc_files,
    use_filesystem)
from compmake.ui.ui import comp, comp_prefix, get_comp_prefix
from quickapp import logger, QUICKAPP_COMPUTATION_ERROR
from quickapp.library.app.quickapp_interface import QuickAppBase
from quickapp.utils import wrap_script_entry_point, UserError
from reprep.report_utils import ReportManager
import contracts
import hashlib
import os
import sys
import warnings
from contracts import contract
from conf_tools.utils import indent
import traceback
from types import NoneType

 
class CompmakeContext():

    @contract(extra_dep='list')    
    def __init__(self, qapp, parent, job_prefix, report_manager, output_dir, extra_dep=[]):
        assert isinstance(qapp, QuickApp)
        assert isinstance(parent, (CompmakeContext, NoneType))
        self._qapp = qapp
        self._parent = parent
        self._job_prefix = job_prefix
        self._report_manager = report_manager
        self._output_dir = output_dir
        self.n_comp_invocations = 0
        self._extra_dep = extra_dep
        self._jobs = {}
        
    def all_jobs(self):
        return list(self._jobs.values())
    
    def comp(self, *args, **kwargs):
        """ 
            Simple wrapper for Compmake's comp function. 
            Use this instead of "comp". """
        self.count_comp_invocations()
        comp_prefix(self._job_prefix)
        extra_dep = self._extra_dep + kwargs.get('extra_dep', [])
        kwargs['extra_dep'] = extra_dep
        promise = comp(*args, **kwargs)
        self._jobs[promise.job_id] = promise
        return promise

    def count_comp_invocations(self):
        self.n_comp_invocations += 1
        if self._parent is not None:
            self._parent.count_comp_invocations()


    def get_output_dir(self):
        """ Returns a suitable output directory for data files """
        # only create output dir on demand
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        return self._output_dir
        
    @contract(extra_dep='list')    
    def child(self, name, qapp=None, add_job_prefix=None, add_outdir=None, extra_dep=[]):
        """ 
            Returns child context 
        
            add_job_prefix = 
                None (default) => use "name"
                 '' => do not add to the prefix
            
            add_outdir:
                None (default) => use "name"
                 '' => do not add outdir               
        """
        if qapp is None:
            qapp = self._qapp
            
        if add_job_prefix is None:
            add_job_prefix = name
            
        if add_outdir is None:
            add_outdir = name
        
        if add_job_prefix != '':
            if self._job_prefix is None:
                job_prefix = name
            else:
                job_prefix = self._job_prefix + '-' + name
        else:
            job_prefix = self._job_prefix
        
        if add_outdir != '':
            output_dir = os.path.join(self._output_dir, name)
        else:
            output_dir = self._output_dir
            
        warnings.warn('add prefix to report manager')
        report_manager = self._report_manager
         
        return CompmakeContext(qapp=qapp, parent=self,
                               job_prefix=job_prefix,
                               report_manager=report_manager,
                               output_dir=output_dir,
                               extra_dep=extra_dep)
    
    def add_report(self, report, report_type=None, **params):
        rm = self.get_report_manager()
        rm.add(report, report_type, **params)


    def get_report_manager(self):
        return self._report_manager
    
    @contract(extra_dep='list')    
    def subtask(self, task, extra_dep=[], **task_config):
        return self._qapp.call_recursive(context=self, child_name=task.cmd,
                                 cmd_class=task, args=task_config,
                                   extra_dep=extra_dep,
                                   add_outdir=None,
                                   add_job_prefix=None)


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
        
        def dict2cmdline(x):
            res = []
            for k, v in x.items():
                res.append('--%s' % k)
                res.append('%s' % v)
            return res
        
        if isinstance(args, dict):
            args = dict2cmdline(args)
            
            
        if isinstance(extra_dep, CompmakeContext):
            extra_dep = extra_dep.all_jobs()
        instance = cmd_class()
        
        instance.parent = self
        is_quickapp = isinstance(instance, QuickApp) 
        
        try:

            # we are already in a context; just define jobs
            child_context = context.child(qapp=self, name=child_name, extra_dep=extra_dep,
                                          add_outdir=add_outdir, add_job_prefix=add_job_prefix)  # XXX
            instance.set_options_from_args(args)

            if not is_quickapp:
                # self.info('Instance is not quickapp! %s' % type(instance))
                self.child_context = child_context
                instance.go()
                return self.child_context
                
            else:
                instance.define_jobs_context(child_context)
                return child_context
        except Exception as e:
            msg = 'Error while trying to call recursive:\n'
            msg += ' class = %s\n' % cmd_class
            msg += ' args = %s\n' % args
            if '_options' in instance.__dict__:
                msg += ' parsed options: %s\n' % instance.get_options()
                msg += ' params: %s\n' % instance.get_options().get_params()
            msg += indent(traceback.format_exc(e), '> ')
            raise Exception(msg)
        
        
# TODO: remove
def create_conf_name_digest(values, length=12):
    """ Create an hash for the given values """
    s = "-".join([str(values[x]) for x in sorted(values.keys())])
    h = hashlib.sha224(s).hexdigest()
    if len(h) > length:
        h = h[:length]
    return h



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
 
 
 
