import os
from types import NoneType
import warnings

from contracts import contract, describe_type

from compmake import Context, Promise
from conf_tools import GlobalConfig

from .report_manager import ReportManager
from .resource_manager import ResourceManager
from compmake.context import load_static_storage


__all__ = ['CompmakeContext']


class CompmakeContext(Context):

    @contract(extra_dep='list')
    def __init__(self, db, qapp, parent, job_prefix,
                 output_dir, extra_dep=[], resource_manager=None,
                 extra_report_keys=None,
                 report_manager=None):
        Context.__init__(self, db=db)
        assert isinstance(parent, (CompmakeContext, NoneType))
        self._qapp = qapp
        self._parent = parent
        self._job_prefix = job_prefix
        
        if resource_manager is None:
            resource_manager = ResourceManager(self)
        
        if report_manager is None:
            self.private_report_manager = True  # only create indexe if this is true
            reports = os.path.join(output_dir, 'reports')
            reports_index = os.path.join(output_dir, 'reports.html')
            report_manager = ReportManager(reports, reports_index)
        else:
            self.private_report_manager = False
        
        self._report_manager = report_manager
        self._resource_manager = resource_manager
        self._output_dir = output_dir
        self.n_comp_invocations = 0
        self._extra_dep = extra_dep
        self._jobs = {}
        if extra_report_keys is None:
            extra_report_keys = {}
        self.extra_report_keys = extra_report_keys
        
        self._promise = None

    def finalize_jobs(self):
        """ After all jobs have been defined, we create index jobs. """
        if self.private_report_manager:
            self.get_report_manager().create_index_job(self)
        
    def __str__(self):
        return 'CC(%s, %s)' % (type(self._qapp).__name__, self._job_prefix)
    
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
    
    #
    # Wrappers form Compmake's "comp".
    #
    @contract(returns=Promise)
    def comp(self, f, *args, **kwargs):
        """ 
            Simple wrapper for Compmake's comp function. 
            Use this instead of "comp". 
        """
        self.count_comp_invocations()
        self.comp_prefix(self._job_prefix)
        extra_dep = self._extra_dep + kwargs.get('extra_dep', [])
        kwargs['extra_dep'] = extra_dep
        promise = Context.comp(self, f, *args, **kwargs)
        self._jobs[promise.job_id] = promise
        return promise
    
    @contract(returns=Promise)
    def comp_config(self, f, *args, **kwargs):
        """ 
            Like comp, but we also automatically save the GlobalConfig state.
        """
        config_state = GlobalConfig.get_state()
        # so that compmake can use a good name
        kwargs['command_name'] = f.__name__
        return self.comp(wrap_state, config_state, f, *args, **kwargs)

    @contract(returns=Promise)
    def comp_dynamic(self, f, *args, **kwargs):
        context = self._get_promise()
        return self.comp(f, context, *args, **kwargs)

    @contract(returns=Promise)
    def comp_config_dynamic(self, f, *args, **kwargs):
        """ Defines jobs that will take a "context" argument to define
            more jobs. """
        config_state = GlobalConfig.get_state()
        # so that compmake can use a good name
        kwargs['command_name'] = f.__name__
        return self.comp_dynamic(wrap_state_dynamic, config_state, f, *args, **kwargs)

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
    def child(self, name, qapp=None,
              add_job_prefix=None,
              add_outdir=None,
              extra_dep=[],
              extra_report_keys=None,
              separate_resource_manager=False,
              separate_report_manager=False):
        """ 
            Returns child context 
        
            add_job_prefix = 
                None (default) => use "name"
                 '' => do not add to the prefix
            
            add_outdir:
                None (default) => use "name"
                 '' => do not add outdir               

            separate_resource_manager: If True, create a child of the ResourceManager,
            otherwise we just use the current one and its context.  
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
        if separate_report_manager:
            if add_outdir == '':
                msg = ('Asked for separate report manager, but without changing output dir. '
                       'This will make the reports overwrite each other.')
                raise ValueError(msg)
                
            report_manager = None
        else:    
            report_manager = self._report_manager
        
        if separate_resource_manager:
            resource_manager = None  # CompmakeContext will create its own
        else:
            resource_manager = self._resource_manager
        
        _extra_dep = self._extra_dep + extra_dep
         
        extra_report_keys_ = {}
        extra_report_keys_.update(self.extra_report_keys)
        if extra_report_keys is not None:
            extra_report_keys_.update(extra_report_keys)
        
        c1 = CompmakeContext(db=self.get_compmake_db(),
                            qapp=qapp, parent=self,
                           job_prefix=job_prefix,
                           report_manager=report_manager,
                           resource_manager=resource_manager,
                           extra_report_keys=extra_report_keys_,
                           output_dir=output_dir,
                           extra_dep=_extra_dep)
        return c1

    @contract(job_id=str)
    def add_job_defined_in_this_session(self, job_id):
        self._jobs_defined_in_this_session.add(job_id)
        if self._parent is not None:
            self._parent.add_job_defined_in_this_session(job_id)

    @contract(extra_dep='list')    
    def subtask(self, task, extra_dep=[], add_job_prefix=None, add_outdir=None,
                    separate_resource_manager=False,
                    separate_report_manager=False,
                    extra_report_keys=None,
                    **task_config):
        return self._qapp.call_recursive(context=self, child_name=task.cmd,
                                         cmd_class=task, args=task_config,
                                         extra_dep=extra_dep,
                                         add_outdir=add_outdir,
                                         add_job_prefix=add_job_prefix,
                                         extra_report_keys=extra_report_keys,
                                         separate_report_manager=separate_report_manager,
                                         separate_resource_manager=separate_resource_manager)

    # Resource managers
    @contract(returns=ResourceManager)
    def get_resource_manager(self):
        return self._resource_manager
    
    def needs(self, rtype, **params):
        # print('%s %s %s %s %s' % (id(self), self._qapp, self._job_prefix, rtype, params))
        rm = self.get_resource_manager()
        res = rm.get_resource(rtype, **params)
        assert isinstance(res, Promise), describe_type(res)
        self._extra_dep.append(res)

    def get_resource(self, rtype, **params):
        rm = self.get_resource_manager()
        return rm.get_resource(rtype, **params)
    
    # Reports    
    @contract(report=Promise, report_type='str')
    def add_report(self, report, report_type, **params):
        rm = self.get_report_manager()
        params.update(self.extra_report_keys)
        rm.add(report, report_type, **params)

    @contract(returns=Promise, report_type='str')
    def get_report(self, report_type, **params):
        """ Returns the promise to the given report """
        rm = self.get_report_manager()
        return rm.get(report_type, **params)

    def get_report_manager(self):
        return self._report_manager
    
    def add_extra_report_keys(self, **keys):
        warnings.warn('check conflict')
        self.extra_report_keys.update(keys)

    @contract(returns=Promise)
    def _get_promise(self):
        """ Returns the promise object representing this context. """
        if self._promise is None:
            warnings.warn('Need IDs for contexts, using job_prefix.')
            self._promise_job_id = 'context'  # -%s' % self._job_prefix
            self._promise = self.comp(load_static_storage, self, job_id=self._promise_job_id)
        return self._promise


def wrap_state(config_state, f, *args, **kwargs):
    """ Used internally by comp_config() """
    config_state.restore()
    return f(*args, **kwargs)


def wrap_state_dynamic(context, config_state, f, *args, **kwargs):
    """ Used internally by comp_config_dynamic() """
    config_state.restore()
    return f(context, *args, **kwargs)

    
def checkpoint(name, prev_jobs):
    pass
