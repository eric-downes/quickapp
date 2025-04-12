"""
Pytest configuration file that applies patches for Python 3 compatibility.
"""
import sys
import os
import types
import importlib.util

# Create a fake imp module before any tests try to import nose
if 'imp' not in sys.modules:
    print("Creating fake imp module for Python 3 compatibility...")
    
    class ImpReplacement:
        @staticmethod
        def find_module(name, path=None):
            """Replacement for imp.find_module using importlib"""
            if path is None:
                path = sys.path
            
            for directory in path:
                if not os.path.isdir(directory):
                    continue
                
                # Check for standard module file
                module_path = os.path.join(directory, name + '.py')
                if os.path.exists(module_path):
                    return (open(module_path, 'r'), module_path, ('.py', 'r', importlib.machinery.SourceFileLoader))
                
                # Check for package
                package_path = os.path.join(directory, name, '__init__.py')
                if os.path.exists(package_path):
                    return (None, os.path.join(directory, name), ('', '', importlib.machinery.SourceFileLoader))
            
            raise ImportError(f"No module named {name}")
        
        @staticmethod
        def load_module(name, file, pathname, description):
            """Replacement for imp.load_module using importlib"""
            suffix, mode, type = description
            
            if file:
                file.close()
            
            if suffix == '.py':
                # Load a source file
                spec = importlib.util.spec_from_file_location(name, pathname)
                if spec is None:
                    raise ImportError(f"Could not load module {name} from {pathname}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                return module
            elif suffix == '':
                # Load a package
                spec = importlib.util.spec_from_file_location(
                    name, os.path.join(pathname, '__init__.py'))
                if spec is None:
                    raise ImportError(f"Could not load package {name} from {pathname}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                return module
            else:
                raise ImportError(f"Unknown module type: {suffix}")
        
        # Dummy lock functions since importlib handles locking internally
        @staticmethod
        def acquire_lock():
            pass
            
        @staticmethod
        def release_lock():
            pass
    
    # Create a fake imp module
    imp_module = types.ModuleType('imp')
    imp_module.find_module = ImpReplacement.find_module
    imp_module.load_module = ImpReplacement.load_module
    imp_module.acquire_lock = ImpReplacement.acquire_lock
    imp_module.release_lock = ImpReplacement.release_lock
    
    # Add it to sys.modules
    sys.modules['imp'] = imp_module

def pytest_configure(config):
    """
    Configure pytest before running tests.
    """
    print("Pytest configuration for Python 3 compatibility loaded")