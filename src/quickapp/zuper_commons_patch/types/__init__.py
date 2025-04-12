#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reimplementation of zuper_commons.types module.
This provides type-related utilities typically found in zuper_commons.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, Type

# Common type variables used in annotations
K = TypeVar('K')
V = TypeVar('V')
X = TypeVar('X')
Y = TypeVar('Y')
Z = TypeVar('Z')
T = TypeVar('T')

# Common composite types
CheckType = Callable[[Any], None]
ClassType = type
GenericDict = Dict[K, V]
GenericList = List[T]
GenericTuple = Tuple

def check_isinstance(obj: Any, expected_type: Type[T]) -> T:
    """
    Check if an object is an instance of the expected type.
    
    Args:
        obj: The object to check
        expected_type: The expected type
        
    Returns:
        The object if it passes the check
        
    Raises:
        TypeError if the object is not an instance of the expected type
    """
    if not isinstance(obj, expected_type):
        msg = f'Expected {expected_type.__name__}, got {type(obj).__name__}: {obj!r}'
        raise TypeError(msg)
    return obj