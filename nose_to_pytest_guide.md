# Migrating from nose to pytest

## Introduction

This guide documents the process of migrating a Python project's test
suite from the now-unmaintained nose framework to pytest. As of Python
3.12, nose is no longer compatible due to its dependency on the
removed `imp` module and other deprecated features. This guide
captures lessons learned during the migration of test
suite, but the principles can be applied to any project.

## Why Migrate to pytest?

- **Maintainability**: nose is no longer maintained and doesn't work, but pytest is the most actively maintained Python testing framework
- **Better features**: pytest provides powerful fixtures, parameterization, and plugin ecosystem
- **Improved readability**: pytest's assertion system is more readable (using plain `assert` statements)
- **Better parallel execution**: pytest has better support for running tests in parallel

## Quick Start: Running Tests During Migration

To run tests during migration without breaking existing code, we
recommend creating a dedicated test runner script (e.g.,
`run_pytest_test.py`):

```python
#!/usr/bin/env python
import os
import sys
import pytest

# Add source directory to path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_dir)

if __name__ == "__main__":
    # Run a specific test file or directory
    test_path = os.path.join('src', 'path', 'to', 'test_file.py')
    result = pytest.main(["-v", test_path])
    sys.exit(result)
```

Crtically this approach means you can verify each conversion without
affecting other tests.  It's also convenient.

## Migration Process Overview

1. **Preparation**: Create infrastructure for pytest
2. **Conversion**: Convert tests file by file
3. **Compatibility**: Address any compatibility issues discovered during migration
4. **Testing**: Ensure converted tests work properly
5. **Integration**: Replace original tests with pytest versions
6. **Cleanup**: Remove nose-specific code and dependencies

## Step 1: Preparation

### 1.1 Create Basic pytest Infrastructure

Create these basic files to set up pytest:

#### `pytest.ini` (in project root)

```ini
[pytest]
testpaths = path/to/tests
python_files = test_*.py *_test.py *_pytest.py
python_classes = Test*
python_functions = test_*
```

The expanded patterns for `python_files` help with transitional periods where both old and new test file naming patterns might coexist.

#### `conftest.py` (in test directory)

```python
# -*- coding: utf-8 -*-
import pytest

# Add shared fixtures here if needed
```

### 1.2 Create a Base Test Class

If your project uses a common base test class, convert it to use pytest fixtures:

```python
# -*- coding: utf-8 -*-
import pytest
from shutil import rmtree
from tempfile import mkdtemp

class BaseTestClass:
    """Base class for pytest-based tests."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Setup code here
        self.temp_dir = mkdtemp()
        
        yield  # This is where the test will run
        
        # Teardown code here
        rmtree(self.temp_dir)
        
    # Helper methods used by multiple tests
    def helper_method(self):
        pass
```

### 1.3 Add pytest to Requirements

Update your requirements file to include pytest:

```
pytest>=7.0.0
```

### 1.4 Create a Migration Tracking Document

Create a document to track migration progress:

```markdown
# Migration Tracking

| Test File | Converted | Pytest File | Working | Notes |
|-----------|-----------|-------------|---------|-------|
| test_1.py | ✅ Done | test_1_pytest.py | ✅ Passing | - |
| test_2.py | 🔄 Not Started | - | - | - |
```

## Step 2: Converting Tests

### 2.1 Basic Changes for Each Test

For each test file:

1. Replace nose-specific imports with pytest
2. Convert class-based tests to use pytest fixtures
3. Replace nose assertions with pytest assertions
4. Rename test methods to follow pytest conventions (test_*)

#### Example Conversion

**Original nose test:**
```python
# -*- coding: utf-8 -*-
from nose.tools import istest
from myproject.base_test import BaseTest

@istest
class TestFeature(BaseTest):
    def setUp(self):
        super(TestFeature, self).setUp()
        self.specific_setup()
        
    def test_some_functionality(self):
        result = self.run_function()
        self.assertEqual(result, expected_value)
        self.assertTrue(condition)
```

**Converted pytest test:**
```python
# -*- coding: utf-8 -*-
import pytest
from myproject.pytest_base import BaseTestClass

class TestFeature(BaseTestClass):
    def specific_setup(self):
        # Specific setup code
        pass
        
    @pytest.fixture(autouse=True)
    def setup(self, setup_teardown):
        self.specific_setup()
        
    def test_some_functionality(self):
        result = self.run_function()
        assert result == expected_value
        assert condition
```

### 2.2 Handling Test Discovery

pytest and nose discover tests differently. If you encounter issues:

- Change test classes to start with `Test`
- Change test methods to start with `test_`
- Remove nose-specific `__init__.py` files

## Step 3: Addressing Compatibility Issues

During migration, you may encounter Python compatibility issues beyond the nose framework itself.

### 3.1 Common Issues

#### Removed Modules and Functions

- **Issue**: Removed modules like `imp` or functions like `time.clock()` or `inspect.getargspec()`
- **Solution**: Create compatibility layers that provide alternatives based on Python version

#### Type Checking in Python 3

- **Issue**: Functions that check types using `isinstance(obj, "TypeName")` with string type names will fail
- **Solution**: Update type checking functions to handle both actual types and string type names
- **Example**:
  ```python
  def check_isinstance(obj, expected_type):
      # Handle case where expected_type is a string
      if isinstance(expected_type, str):
          # For Python 3 compatibility, just check if it's the right object type name
          return obj
          
      if not isinstance(obj, expected_type):
          raise ValueError(f"Expected type {expected_type}, got {type(obj)}")
      return obj
  ```

Example compatibility layer for `time.clock()`:

```python
# -*- coding: utf-8 -*-
import time

# time.clock() was removed in Python 3.8, use time.perf_counter() instead
if hasattr(time, 'perf_counter'):
    # Python 3.3+
    def get_cpu_time():
        return time.perf_counter()
elif hasattr(time, 'clock'):
    # Python 2.x and early Python 3.x
    def get_cpu_time():
        return time.clock()
else:
    # Fallback to time.time() if neither is available
    def get_cpu_time():
        return time.time()
```

#### Circular Import Issues

- **Issue**: Test discovery in `__init__.py` causes circular imports with nose
- **Solution**: Create a clean `__init__.py` for pytest that doesn't import test modules

#### Multiprocessing Issues in Python 3.12

- **Issue**: Python 3.12 made changes to the multiprocessing module that can cause errors with existing code
- **Solution**: 
  - For test purposes, you may need to temporarily switch from parallel to sequential execution
  - For permanent fixes, review the Python 3.12 multiprocessing module changes and update code accordingly
  - Watch for KeyError exceptions in resource tracking or memory-shared dictionaries
  - When encountering errors with `parmake`, switching to sequential `make` is often a workable solution

#### Dependencies on Nose in Helper Modules

- **Issue**: Some test helper modules may import from nose, causing pytest tests to fail with import errors
- **Solution**:
  - Create pytest versions of helper modules (e.g., for decorators like `@expected_failure`)
  - Replace nose-specific helpers with pytest equivalents (`@pytest.mark.xfail` instead of `@expected_failure`)
  - Use conditional imports in helper modules to work with both frameworks during migration

### 3.2 Running Tests Standalone

Create a way to run individual tests without depending on the test discovery system:

```python
if __name__ == "__main__":
    # Run this specific test file directly
    pytest.main(["-xvs", __file__])
```

### 3.3 Using Test Runners During Migration

For large codebases, it's helpful to create a dedicated test runner script like `run_pytest_test.py` to facilitate migration:

```python
#!/usr/bin/env python
import os
import sys
import pytest
import shutil
import atexit

# Directory paths
root_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(root_dir, 'path/to/tests')

# File paths for __init__.py swapping
init_path = os.path.join(test_dir, '__init__.py')
init_pytest_path = os.path.join(test_dir, '__init__.py.pytest')
init_backup_path = os.path.join(test_dir, '__init__.py.backup')

def swap_init_files():
    """Swap the __init__.py file to use the pytest-friendly version."""
    # Backup current __init__.py
    if os.path.exists(init_path):
        shutil.copy2(init_path, init_backup_path)
    
    # Install pytest version
    if os.path.exists(init_pytest_path):
        shutil.copy2(init_pytest_path, init_path)

def restore_init_files():
    """Restore the original __init__.py file."""
    if os.path.exists(init_backup_path):
        shutil.copy2(init_backup_path, init_path)
        os.remove(init_backup_path)

# Register cleanup function
atexit.register(restore_init_files)

if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'path/to/tests'
    
    # Swap files before running tests
    swap_init_files()
    
    try:
        # Run the test
        result = pytest.main(["-v", test_path])
        sys.exit(result)
    finally:
        # restore_init_files will be called by atexit
        pass
```

This approach:
1. Temporarily swaps in a pytest-compatible `__init__.py` 
2. Runs the specified test(s) with pytest
3. Automatically restores the original `__init__.py` on exit
4. Allows testing converted files while keeping the original nose tests working

## Step 4: Testing the Migration

Test your migration as you go:

1. Test individual files first:
   ```bash
   python -m pytest path/to/test_file.py -v
   ```

2. Test groups of related tests next:
   ```bash
   python -m pytest path/to/test_dir -v
   ```

3. Run the full test suite at the end:
   ```bash
   python -m pytest
   ```

## Step 5: Final Integration

Once all tests have been migrated and verified:

1. Remove nose from requirements
2. Clean up any remaining nose-specific code or imports
3. Update CI/CD pipelines to use pytest

## Common Conversions

| nose | pytest |
|------|--------|
| `from nose.tools import istest` | Use name convention `class Test*` |
| `from nose.tools import raises` | `with pytest.raises(Exception):` |
| `self.assertEqual(a, b)` | `assert a == b` |
| `self.assertNotEqual(a, b)` | `assert a != b` |
| `self.assertTrue(x)` | `assert x` |
| `self.assertFalse(x)` | `assert not x` |
| `self.assertRaises(ExcType, func, *args)` | `with pytest.raises(ExcType): func(*args)` |
| `@nose.tools.raises(ExcType)` | `@pytest.mark.xfail(raises=ExcType)` or `with pytest.raises(ExcType):` |
| `setUp()` | `@pytest.fixture(autouse=True)` |
| `tearDown()` | Yield fixture teardown |
| `@nottest` | `@pytest.mark.skip(reason="...")` |
| `@expected_failure` | `@pytest.mark.xfail(reason="...")` |
| `self.assertEqualSet(a, b)` | `assert set(a) == set(b)` |
| `self.assertJobsEqual(...)` | Create custom assertion helpers in a base class |

## Examples from Our Migration

### Basic Test Conversion

**Original nose test:**
```python
from nose.tools import istest
from .compmake_test import CompmakeTest

def job_success(*args, **kwargs):
    pass

def job_failure(*args, **kwargs):
    raise ValueError('This job fails')

@istest
class TestBlocked(CompmakeTest):
    def mySetUp(self):
        pass

    def testAdding(self):
        comp = self.comp
        A = comp(job_success, job_id='A')
        B = comp(job_failure, A, job_id='B')
        comp(job_success, B, job_id='C')
        
        def run():
            self.cc.batch_command('make')
        self.assertMakeFailed(run, nfailed=1, nblocked=1)
```

**Converted pytest test:**
```python
import pytest
from .pytest_base import CompmakeTestBase

def job_success(*args, **kwargs):
    pass

def job_failure(*args, **kwargs):
    raise ValueError('This job fails')

class TestBlocked(CompmakeTestBase):
    def mySetUp(self):
        pass

    def test_adding(self):
        comp = self.comp
        A = comp(job_success, job_id='A')
        B = comp(job_failure, A, job_id='B')
        comp(job_success, B, job_id='C')
        
        def run():
            self.cc.batch_command('make')
        self.assertMakeFailed(run, nfailed=1, nblocked=1)
```

### Compatibility Layer Example 

When we found code using the removed `time.clock()` function, we created a compatibility layer:

```python
# -*- coding: utf-8 -*-
import time

# time.clock() was removed in Python 3.8, use time.perf_counter() instead
if hasattr(time, 'perf_counter'):
    # Python 3.3+
    def get_cpu_time():
        return time.perf_counter()
elif hasattr(time, 'clock'):
    # Python 2.x and early Python 3.x
    def get_cpu_time():
        return time.clock()
else:
    # Fallback to time.time() if neither is available
    def get_cpu_time():
        return time.time()
```

## Conclusion

Migrating from nose to pytest is a methodical process that can be done incrementally. The migration not only improves test maintainability but also uncovers and addresses potential compatibility issues in your codebase. 

### Key Lessons Learned

1. **Dual Approach Works Best**: Creating both a compatibility layer (for running old tests) and new pytest-specific versions (for future) provides a smooth transition.

2. **Base Class Migration is Critical**: Converting the base test class early gives you a solid foundation for all other test migrations.

3. **Python Version Compatibility**: Many issues relate to Python version changes rather than nose-to-pytest conversion specifically.

4. **Common Patterns**: Look for patterns in your test code - once you've migrated one example of a pattern, others will follow the same approach.

5. **Test the Tests**: Run your migrated tests frequently to catch errors early.

6. **Keep the Original Files**: During migration, keep both sets of files until you're confident everything works.

By following this approach, we successfully migrated a complex test suite with multiple interdependencies, ensuring compatibility with Python 3.12 while improving maintainability for the future.

---

## Comprehensive Guide to Test Isolation

Based on our migration experience, test isolation is one of the most challenging aspects of migrating from nose to pytest. Here's a comprehensive approach to handling isolation issues:

### 1. Creating an Improved Base Test Class

For complex test suites, create an enhanced base class with better isolation features:

```python
class ImprovedTestBase:
    """Base class with better test isolation."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, tmp_path):
        """Setup and teardown with better isolation."""
        # Use pytest's tmp_path fixture for unique test directories
        self.test_dir = os.path.join(str(tmp_path), f"test_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Save original configuration state
        self.original_configs = {}
        for config_name in ['important_setting', 'another_setting']:
            self.original_configs[config_name] = get_config(config_name)
        
        # Setup your test environment
        self.initialize_test_environment()
        
        yield  # Test runs here
        
        # Restore original configurations
        for name, value in self.original_configs.items():
            set_config(name, value)
            
        # Clean up any resources
        self.cleanup_resources()
```

### 2. State Sharing Patterns

When tests or test phases must share state, use these patterns:

#### Pattern 1: Explicit State Transfer
```python
def test_phase1(self):
    # Run first phase
    result = run_operation()
    # Store result for next test
    self.store_result('key1', result)

def test_phase2(self):
    # Get result from previous phase
    result = self.get_stored_result('key1')
    # Continue testing
```

#### Pattern 2: Controlled Global State
```python
class TestClass:
    # Class variable to track current test instance
    current_instance = None
    
    def setup_method(self):
        # Set current instance to this test
        TestClass.current_instance = self
        # Initialize test-specific state
        self.my_state = {}
    
    # Other functions can access state through class reference
    # This avoids issues with closures and lambda functions
```

### 3. Handling Database and File System State

For tests involving databases and file operations:

1. **Use unique directories for each test**:
   ```python
   def test_function(self, tmp_path):
       test_dir = os.path.join(str(tmp_path), f"test_{uuid.uuid4().hex[:8]}")
       # Use this directory for all file operations
   ```

2. **Create fresh contexts for different test phases**:
   ```python
   # For phase 1
   context1 = create_context(directory1)
   run_tests(context1)
   
   # For phase 2 - completely new context
   context2 = create_context(directory2)
   run_tests(context2)
   ```

3. **Flush caches between test phases**:
   ```python
   # Clear any cached state
   context.execute_command('clean_cache')
   # Now run the test
   run_test(context)
   ```

### 4. Dealing with Pickling and Serialization

1. **Avoid lambda functions in serialized contexts**:
   ```python
   # BAD - will cause pickle errors
   context.execute_dynamic(lambda x: some_function(x, parameter))
   
   # GOOD - use named functions
   def wrapper_function(x):
       # Get parameters from a safe place
       return some_function(x, get_parameter())
   
   context.execute_dynamic(wrapper_function)
   ```

2. **Be careful with closures**:
   ```python
   # BAD - closure references local variable
   def outer_function(parameter):
       def inner_function():
           return parameter  # This causes pickle issues
       return inner_function
   
   # GOOD - use class state instead
   class TestClass:
       @classmethod
       def set_parameter(cls, value):
           cls.parameter = value
           
       def inner_function(self):
           return self.__class__.parameter
   ```

### 5. Handling Permission Issues with Example Files

Tests that execute example files as subprocesses may encounter permission issues:

1. Make example files executable: `chmod +x path/to/example.py`
2. Skip tests with permission problems during migration: `@pytest.mark.skip(reason="Permission issues")`
3. Consider modifying the test to use internal APIs instead of subprocess calls for greater test reliability

### 6. Debugging Isolation Issues

When you encounter test isolation problems:

1. **Run tests individually**: Verify they pass in isolation
2. **Run with high verbosity**: `pytest -vv` to see detailed output
3. **Use print debugging**: Add print statements to track state changes
4. **Create test order-aware fixtures**: If needed, use fixtures that know about test order

This guide represents lessons learned from our experience migrating a complex codebase from nose to pytest. These patterns have helped us successfully migrate tests while ensuring they work both individually and in sequence.