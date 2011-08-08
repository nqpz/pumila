#!/usr/bin/env python3

# pumila: convert images to sound waves
# Copyright (C) 2011 Niels Serup

# This file is part of pumila.

# pumila is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pumila is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pumila.  If not, see <http://www.gnu.org/licenses/>.

"""
Misc. objects.
"""

import sys
import os
import locale
import datetime
import time
import email.utils
import itertools
import functools
import collections
import atexit
import traceback

preferred_encoding = locale.getpreferredencoding()

####################
# Helper functions #
####################
class Container:
    pass

class AttributeDict(dict):
    """A dictionary where x.a == x['a']"""
    def __init__(self, *args, **kwds):
        self._to_apply=kwds.get('to_apply')
        self._apply_what=kwds.get('apply_what')
        if args:
            kwds = {}
            nkwds = self._init(args, {})
            for k, v in nkwds.items():
                kwds[k] = v
        dict.__init__(self, **kwds)

    def _init(self, args, kwds):
        nkwds = AttributeDict()
        for i in range(0, len(args), 2):
            k, v = args[i:i + 2]
            rv = None
            if isinstance(v, list):
                v = self._init(v, kwds)
            else:
                if isinstance(v, str):
                    v = v.format(**kwds)
                if self._to_apply and (self._apply_what is None or
                                       type(v) in self._apply_what):
                    rv = self._to_apply(v)
            if not rv: rv = v
            kwds[k] = v
            nkwds[k] = rv
        return nkwds

    __getattr__ = lambda self, k: self.__getitem__(k)
    __setattribute__ = lambda self, k, v: self.__setitem__(k, v) \
        if not k.startswith('_') else None
    __delattr__ = lambda self, k: tryorpass(KeyError, self.__delitem__, k)

    def __setstate__(self, adict):
        for k, v in adict.items():
            self.__setitem__(k, v)

class PeriodTextTuple(tuple):
    """A tuple meant for version numbers"""
    def __init__(self, *args):
        self.text = '.'.join(str(x) for x in self)

    __new__ = lambda self, *xs: tuple.__new__(self, xs)
    __str__ = lambda self: self.text

def tryorpass(exceptions, func=None, *args, **kwds):
    """
    Try to execute a function. Pass if an exception of exceptions is raised.

    If func returns an iterable, all elements will be tested individually. This
    function can be used as a decorator.
    """
    if not func: # Act as decorator
        nfunc = lambda func: tryorpass(exceptions, func, *args, **kwds)
        kwds['return_func'] = nfunc
        return nfunc
    return_func = kwds.get('return_func')
    if return_func:
        del kwds['return_func']
        return_func.__name__ = func.__name__
        return_func.__doc__ = func.__doc__
    _return = lambda r=None: r if not return_func else return_func
    try:
        ret = func(*args, **kwds)
    except exceptions:
        return _return()
    try:
        rets = iter(ret)
    except TypeError:
        return _return(ret)
    rets_list = []
    while True:
        try:
            temp = next(rets)
        except StopIteration:
            break
        except exceptions:
            continue
        rets_list.append(temp)
    return _return(rets_list)

def is_acceptable_file(path):
    """
    Return True if path is file and does not end with '~' or '.py[co]?', else
    False.
    """
    if not os.path.isfile(path):
        return False
    for x in ('~', '.py', '.pyc', '.pyo'):
        if path.endswith(x):
            return False
    return True

def callable(obj):
    """Return True if obj is callable, else False."""
    return isinstance(obj, collections.Callable)

def get_selfdict(name):
    """Get the globals of a module"""
    return sys.modules[name].__dict__

donothing = lambda *x, **y: None

###########
# Logging #
###########

def dateformat(dt=None, localtime=True):
    """Format a date according to RFC 2822"""
    return email.utils.formatdate(
        timeval=time.mktime(dt.timetuple()) if dt else None,
        localtime=localtime)

_logfile, _logfileclose = sys.stderr, lambda: _logfile.close()
_altlogfile, _altlogfileclose = None, lambda: _altlogfile.close()
_log_levels = ('notice', 'warning', 'error')
def log(*message, **kwds):
    """Write a message to the log"""
    level, module, trace = kwds.get('level'), kwds.get('module'), \
        kwds.get('traceback')
    if level is None:
        if kwds.get('error'):
            level = 2
        elif kwds.get('warning'):
            level = 1
        else:
            level = 0
    for k in ('level', 'module', 'error', 'warning', 'traceback'):
        try: del kwds[k]
        except KeyError: pass
    sep = kwds.get('sep', ' ')
    if _logfile or _altlogfile:
        text = '[{}] [{}] {}{}'.format(
            dateformat(), _log_levels[level], '({}) '.format(
                module) if module else '', sep.join(map(str, message)))
        if trace:
            text += '\n' + format(traceback.format_exc())
        for o in (_logfile, _altlogfile):
            if o:
                kwds['file'] = o
                print(text, **kwds)

def newlog(module_name=''):
    """Create a new log function with a module's name"""
    return functools.partial(log, module=module_name)

def setlogfile(fobj=None, close_on_exit=None, alt=False):
    """Set the output file of the log file"""
    global _logfile, _altlogfile
    if fobj is None:
        fobj = sys.stderr
    if close_on_exit is None:
        if fobj in (sys.stderr, sys.stdout):
            close_on_exit = False
    else:
        close_on_exit = True

    if isinstance(fobj, str):
        if not alt:
            _logfile = open(fobj, 'w')
        else:
            _altlogfile = open(fobj, 'w')
    else:
        if not alt:
            _logfile = fobj
        else:
            _altlogfile = fobj
    lclose = _logfileclose if not alt else _altlogfileclose
    if close_on_exit:
        atexit.register(lclose)
    else:
        atexit.unregister(lclose)

def setnologfile():
    """Do not log"""
    global _logfile
    _logfile = None
    atexit.unregister(_logfileclose)

def setaltlogfile(fobj, close_on_exit=None):
    """Set the alternative output file of the log file"""
    setlogfile(fobj, close_on_exit, alt=True)

