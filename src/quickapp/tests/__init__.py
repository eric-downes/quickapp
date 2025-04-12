"""
Test utilities for Python 3 compatibility.
"""

# Create a simple istest decorator that can replace nose.tools.istest
def istest(cls):
    """
    Decorator to mark a class as a test (replacement for nose.tools.istest).
    This marks the decorated class as a test by setting the __test__ attribute to True.
    """
    cls.__test__ = True
    return cls