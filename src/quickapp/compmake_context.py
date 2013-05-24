from .resource_manager import ResourceManager
from .report_manager import ReportManager
from compmake import Promise, comp, comp_prefix
from contracts import contract, describe_type
from types import NoneType
import os
import warnings
from conf_tools.master import GlobalConfig

__all__ = ['CompmakeContext']


class CompmakeContext():

    @contract(extra_dep='list', report_manager=ReportManager,
              resource_manager=ResourceManager)    
    def __init__(self, qapp, parent, job_prefix, report_manager, resource_manager,
                 output_dir, extra_dep=[]):
        assert isinstance(parent, (CompmakeContext, NoneType))
        self._qapp = qapp
        self._parent = parent
        self._job_prefix = job_prefix
        self._report_manager = report_manager
        self._resource_manager = resource_manager
        self._output_dir = output_dir
        self.n_comp_invocations = 0
        self._extra_dep = extra_dep
        self._jobs = {}
        
    def all_jobs(self):
        return list(self._jobs.values())
    
    def all_jobs_dict(self):
        return dict(self._jobs)
    
    @contract(job_name='str', returns=Promise)
    def checkpoint(self, job_name):
        """ 
            Creates a dummy job called "job_name" that depends on all jobs
            previously defined; further, this new job is put into _extra_dep.
            This means that all successive jobs will require that the previous 
            ones be done.
            
            Returns the checkpoint job (CompmakePromise).
        """
        job_checkpoint = self.comp(checkpoint, job_name, prev_jobs=list(self._jobs.values()),
                                   job_id=job_name)
        self._extra_dep.append(job_checkpoint)
        return job_checkpoint
    
    @contract(returns=Promise)
    def comp(self, f, *args, **kwargs):
        """ 
            Simple wrapper for Compmake's comp function. 
            Use this instead of "comp". """
        self.count_comp_invocations()
        comp_prefix(self._job_prefix)
        extra_dep = self._extra_dep + kwargs.get('extra_dep', [])
        kwargs['extra_dep'] = extra_dep
        promise = comp(f, *args, **kwargs)
        self._jobs[promise.job_id] = promise
        return promise
    
    @contract(returns=Promise)
    def comp_config(self, f, *args, **kwargs):
        """ 
            We automatically save the GlobalConfig state.
        """
        config_state = GlobalConfig.get_state()
        # so that compmake can use a good name
        kwargs['command_name'] = f.__name__
        return self.comp(wrap_state, config_state, f, *args, **kwargs)
    
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
            
        name_friendly = name.replace('-', '_')
        
        if add_job_prefix is None:
            add_job_prefix = name_friendly
            
        if add_outdir is None:
            add_outdir = name_friendly
        
        if add_job_prefix != '':            
            if self._job_prefix is None:
                job_prefix = add_job_prefix
            else:
                job_prefix = self._job_prefix + '-' + add_job_prefix
        else:
            job_prefix = self._job_prefix
        
        if add_outdir != '':
            output_dir = os.path.join(self._output_dir, name)
        else:
            output_dir = self._output_dir
            
        warnings.warn('add prefix to report manager')
        report_manager = self._report_manager
        resource_manager = self._resource_manager
        
        _extra_dep = self._extra_dep + extra_dep
         
        return CompmakeContext(qapp=qapp, parent=self,
                               job_prefix=job_prefix,
                               report_manager=report_manager,
                               resource_manager=resource_manager,
                               output_dir=output_dir,
                               extra_dep=_extra_dep)

    @contract(extra_dep='list')    
    def subtask(self, task, extra_dep=[], add_job_prefix=None, add_outdir=None, **task_config):
        return self._qapp.call_recursive(context=self, child_name=task.cmd,
                                         cmd_class=task, args=task_config,
                                         extra_dep=extra_dep,
                                         add_outdir=add_outdir,
                                         add_job_prefix=add_job_prefix)

    # Resource managers
    def get_resource_manager(self):
        return self._resource_manager
    
    def needs(self, rtype, **params):
        rm = self.get_resource_manager()
        res = rm.get_resource(rtype, **params)
        assert isinstance(res, Promise), describe_type(res)
        self._extra_dep.append(res)

    # Reports    
    def add_report(self, report, report_type=None, **params):
        rm = self.get_report_manager()
        rm.add(report, report_type, **params)

    def get_report_manager(self):
        return self._report_manager

def wrap_state(config_state, f, *args, **kwargs):
    config_state.restore()
    return f(*args, **kwargs)
    
    
def checkpoint(name, prev_jobs):
    pass
