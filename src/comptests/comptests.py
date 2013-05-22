from conf_tools import import_name
from quickapp import QuickApp

__all__ = ['CompTests']


class CompTests(QuickApp):
    """ 
        Runs the modules tests using compmake as a backend. 
        
        
    """ 

    cmd = 'compmake-tests'

    function_name = 'get_comptests'

    def define_options(self, params):
        params.accept_extra()
         
    
    def define_jobs_context(self, context):
        modules = self.options.get_extra()
        if not modules:
            raise ValueError('No modules given')

        for m in modules:
            self.define_jobs_module(context.child(m), m)
            
    def define_jobs_module(self, context, module_name):            
        module = import_name(module_name)
        f = CompTests.function_name
        if not f in module.__dict__:
            msg = 'Module %s does not have function %s().' % (module_name, f)
            self.error(msg)
        
        ff = module.__dict__[f]
        for f in ff():
            context.subtask(f)
        

main_comptests = CompTests.get_sys_main()
