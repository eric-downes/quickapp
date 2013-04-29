from collections import defaultdict
from compmake import Promise
from contracts import contract, describe_type
from reprep.report_utils import StoreResults


class ResourceManager():
    
    def __init__(self, context):
        self.allresources = StoreResults()
        self.providers = defaultdict(list)
        self.context = context
        
    @contract(rtype='str')
    def set_resource_provider(self, rtype, provider):
        """
            provider: any callable. It will be called with "context" as first 
                argument, and with any remaining params.
        """
        self.providers[rtype].append(provider)  # TODO: list

    @contract(rtype='str')
    def get_resource(self, rtype, **params):
        key = dict(rtype=rtype, **params)
        already_done = key in self.allresources
        if already_done:
            return self.allresources[key]
        else:
            if not rtype in self.providers:
                msg = 'Could not find resource type %r.' % rtype
                raise ValueError(msg)
            
            prefix = self._make_prefix(rtype, **params)    
            c = self.context.child(name=rtype, add_job_prefix=prefix, add_outdir=rtype)
            
            errors = []
            for provider in self.providers[rtype]:
                try:
                    res = provider(c, **params)
                    break
                except ResourceManager.CannotProvide as e:
                    errors.append(e)
            else:
                msg = 'No provider could create this resource.'
                msg += errors
                raise 
            
            self.set_resource(res, rtype, **params)
            return res
    
    class CannotProvide(Exception):
        pass
    
    def _make_prefix(self, rtype, **params):
        """ Creates the job prefix for the given resource. """
        keys = sorted(list(params.keys()))
        vals = [params[k] for k in keys]
        rtype = rtype.replace('-', '_')
        alls = [rtype] + vals
        prefix = "-".join(alls)
        return prefix
        
    @contract(rtype='str')
    def set_resource(self, goal, rtype, **params):
        key = dict(rtype=rtype, **params)
        if not isinstance(goal, Promise):
            msg = 'Warning, resource %s' % key
            msg += ' has type %s' % describe_type(goal)
            # logger.error(msg)
            raise ValueError(msg)
        
        self.allresources[key] = goal
         
