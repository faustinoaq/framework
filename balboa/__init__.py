"""
Balboa Framework

Balboa is a minimalistic web framework for Python 3.10+.
It is designed to be simple, lightweight, and easy to use.
It uses Python's new async/await syntax to handle requests.
Also new matching syntax is used to match events.
"""

from .core import *

# from .core import get, post, put, patch, delete, head, options, run, framework

# __all__ = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'run', 'framework']

# import sys
# from . import core

# class Callable:
#     def __init__(self, module):
#         for attr_name in dir(module):
#             attr = getattr(module, attr_name)
#             if callable(attr):
#                 setattr(self, attr_name, attr)

#     def __call__(self):
#         return framework

# sys.modules[__name__] = Callable(core)