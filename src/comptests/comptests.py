from conf_tools import import_name
from quickapp import QuickApp
import os
from os.path import dirname, exists, join
from conf_tools.utils import locate_files

__all__ = ['CompTests', 'main_comptests']


class CompTests(QuickApp):
    """ 
        Runs the modules tests using compmake as a backend. 
        
        
    """ 

    cmd = 'compmake-tests'

    function_name = 'get_comptests'

    def define_options(self, params):
        params.accept_extra()
         
    
    def define_jobs_context(self, context):
        for m in self.interpret_extras_as_modules():
            c = context.child(m)
            self.define_jobs_module(c, m)
            
    def interpret_extras_as_modules(self):
        """ yields a list of modules """ 
        extras = self.options.get_extra()
        if not extras:
            raise ValueError('No modules given')

        for m in extras:
            if os.path.exists(m):
                # if it's a path, look for 'setup.py' subdirs
                self.info('Interpreting %r as path.' % m)
                modules = list(find_modules(m))
                if not modules:
                    self.warn('No modules found in %r' % m)
                
                for m in modules:
                    yield m
            else:
                self.info('Interpreting %r as module.' % m)
                yield m
                
            
    def look_for_packages(self, d):
        setups = locate_files(d, 'setup.py')
        for s in setups:
            # look for '__init__.py'
            base = join(dirname(s), 'src')
            for i in locate_files(base, '__init__.py'):
                p = os.path.relpath(i, base)
                components = p.split('/')[:-1]  # remove __init__
                module = ".".join(components)
                yield module
        
    def define_jobs_module(self, context, module_name):
        is_first = not '.' in module_name
        warn_errors = is_first
        try:            
            module = import_name(module_name)
        except ValueError as e:
            if warn_errors:
                self.error(e)  # 'Could not import %r: %s' % (module_name, e))
            return
        
        f = CompTests.function_name
        if not f in module.__dict__:
            msg = 'Module %s does not have function %s().' % (module_name, f)
            if warn_errors: 
                self.warn(msg)
            return
        
        ff = module.__dict__[f]
        for f in ff():
            context.subtask(f)
        

def find_modules(d):
    """ 
        Looks for modules defined in packages that have the structure: ::
        
            dirname/setup.py
            dirname/src/
            dirname/src/module/__init__.py
            dirname/src/module/module2/__init__.py
            
        This will yield ['module', 'module.module2']
    """ 
    setups = locate_files(d, 'setup.py')
    for s in setups:
        # look for '__init__.py'
        base = join(dirname(s), 'src')
        for i in locate_files(base, '__init__.py'):
            p = os.path.relpath(i, base)
            components = p.split('/')[:-1]  # remove __init__
            module = ".".join(components)
            yield module
            
            
main_comptests = CompTests.get_sys_main()
