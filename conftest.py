"""
Root pytest configuration file that applies patches for Python 3 compatibility.
"""
import sys
import os
import types
import importlib.util

# Create a more comprehensive patching system for Python 3.12 compatibility
print("Creating Python 3.12 compatibility patches (root conftest.py)...")

# 1. Patch the imp module
if 'imp' not in sys.modules:
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
    print("Added 'imp' module compatibility patch")

# 2. Patch unittest._TextTestResult
# In Python 3.12, unittest no longer has _TextTestResult, but uses TextTestResult
import unittest
from unittest.runner import TextTestResult
import inspect

# Patch inspect.getargspec for Python 3.12
if not hasattr(inspect, 'getargspec'):
    # Create a compatibility wrapper around the newer inspect.getfullargspec
    def getargspec(func):
        """
        Get the names and default values of a function's parameters.
        
        This is a compatibility wrapper for the deprecated inspect.getargspec
        using the newer inspect.getfullargspec in Python 3.
        """
        spec = inspect.getfullargspec(func)
        return inspect.ArgSpec(
            args=spec.args,
            varargs=spec.varargs,
            keywords=spec.varkw,
            defaults=spec.defaults
        )
    
    # Add the function to the inspect module
    inspect.getargspec = getargspec
    print("Patched inspect.getargspec with inspect.getfullargspec wrapper")

if not hasattr(unittest, '_TextTestResult'):
    # Make _TextTestResult available in the unittest module
    unittest._TextTestResult = TextTestResult
    print("Patched unittest._TextTestResult")

# 3. Provide a custom nose compatibility layer
if 'nose' not in sys.modules:
    # Create a simple nose.tools module with needed functions
    nose_module = types.ModuleType('nose')
    nose_tools_module = types.ModuleType('nose.tools')
    
    def istest(cls):
        """Simple implementation of nose.tools.istest that makes a class discoverable by pytest"""
        cls.__test__ = True
        return cls
        
    def nottest(func):
        """Simple implementation of nose.tools.nottest that makes a function not discoverable by pytest"""
        func.__test__ = False
        return func
    
    # Add assertion functions from pytest
    def assert_equals(a, b, msg=None):
        assert a == b, msg or f"{a} != {b}"
        
    def assert_true(expr, msg=None):
        assert expr, msg or f"Expression is not True: {expr}"
        
    def assert_false(expr, msg=None):
        assert not expr, msg or f"Expression is not False: {expr}"
        
    # Add the raises decorator (similar to pytest.raises)
    def raises(exception):
        """Decorator to assert that a test raises a specific exception"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    func(*args, **kwargs)
                except exception:
                    # Exception was raised as expected
                    return
                except Exception as e:
                    # Wrong exception was raised
                    assert False, f"Expected {exception.__name__}, but got {type(e).__name__}: {e}"
                # No exception was raised
                assert False, f"Expected {exception.__name__} to be raised, but no exception was raised"
            return wrapper
        return decorator
    
    # Add these functions to nose.tools
    nose_tools_module.istest = istest
    nose_tools_module.nottest = nottest
    nose_tools_module.assert_equals = assert_equals
    nose_tools_module.assert_true = assert_true
    nose_tools_module.assert_false = assert_false
    nose_tools_module.raises = raises
    
    # Add common aliases used in the codebase
    nose_tools_module.eq_ = assert_equals
    
    # Build the basic core parts of nose to avoid deeper imports
    nose_core = types.ModuleType('nose.core')
    nose_core.collector = lambda: None
    nose_core.main = lambda: None
    nose_core.run = lambda: None
    nose_core.run_exit = lambda: None
    nose_core.runmodule = lambda: None
    
    # Add other necessary modules
    sys.modules['nose.tools'] = nose_tools_module
    sys.modules['nose'] = nose_module
    sys.modules['nose.core'] = nose_core
    
    print("Added more comprehensive nose compatibility patch")

# Optional: Add a lighter option to completely disable nose tests
DISABLE_NOSE_TESTS = False  # Set to True to skip nose-based tests

if DISABLE_NOSE_TESTS:
    # This will make nose.tools.istest a no-op that hides tests from pytest
    from unittest import SkipTest
    def istest_disabled(cls):
        # Make test classes using this decorator get skipped
        if not hasattr(cls, '__test__'):
            cls.__test__ = False
        return cls
    
    if 'nose.tools' in sys.modules:
        sys.modules['nose.tools'].istest = istest_disabled
        print("Disabled nose-based tests")

def pytest_configure(config):
    """
    Configure pytest before running tests.
    """
    # Configure custom test collection 
    
def pytest_collection_modifyitems(items):
    """
    Modify collected items to include unittest methods that don't follow pytest naming conventions.
    """
    # Look for methods in unittest classes that follow unittest-style naming (test* or *_test*)
    # but not pytest-style (test_*)
    for item in list(items):
        if hasattr(item, 'cls') and item.cls is not None and hasattr(item.cls, '__mro__'):
            try:
                if issubclass(item.cls, unittest.TestCase):
                    module = item.cls.__module__
                    classname = item.cls.__name__
                    # Add all methods from the class that look like tests but don't start with 'test_'
                    for name in dir(item.cls):
                        if (name.startswith('test') or '_test' in name) and not name.startswith('test_'):
                            print(f"Found non-standard test method: {classname}.{name}")
            except TypeError:
                # Skip if the class is not actually a class
                pass
    print("Pytest root configuration for Python 3 compatibility loaded")