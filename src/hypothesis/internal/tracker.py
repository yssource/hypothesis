# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2017 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

from hypothesis.utils.conventions import UniqueIdentifier
from hypothesis.internal.compat import text_type, binary_type, integer_types
import sys  # noqa
from hypothesis.internal.compat import getfullargspec, HAS_MATMUL
from weakref import WeakKeyDictionary

comparison = UniqueIdentifier("comparison")
origin = UniqueIdentifier("origin")


def label_for(other):
    if isinstance(other, SAFE_LABEL_TYPES):
        return other
    elif isinstance(other, BaseTracker):
        return (BaseTracker, other._self_name)
    else:
        caller = sys._getframe(2)
        return (origin, caller.f_code.co_filename, caller.f_lineno)


def record(self, operator, value):
    self._self_data.add_tag((comparison, self._self_name, operator, value))


def unwrap(other):
    if isinstance(other, BaseTracker):
        return other.__wrapped__
    return other


SAFE_LABEL_TYPES = (
    text_type, binary_type, bool, complex, float,
) + integer_types


DUNDER_METHOD = """
def %(method)s(self, %(args)s):
    return type(self.__wrapped__).%(method)s(self.__wrapped__, %(args)s)
"""

DUNDER_PROPERTY = """
@property
def %(name)s(self):
    return self.__wrapped__.%(name)s
"""

BINARY_OPERATOR = """
def %(name)s(self, other):
    if isinstance(other, Tracker):
        result = %(expr)s
        return Tracker(
            result, "%%s %(op)s %%s" %% (
                self._self_name, other._self_name,
            ), self._self_data,
        )
    else:
        return type(self.__wrapped__).%(name)s(self.__wrapped__, other)
"""

DUNDER_METHODS_FOR_OPERATORS = [
    ('add', '+'),
    ('sub', '-'),
    ('mul', '*'),
    ('truediv', '/'),
    ('floordiv', '//'),
    ('mod', '%'),
    ('lshift', '<<'),
    ('rshift', '>>'),
    ('and', '&'),
    ('xor', '^'),
    ('or', '|'),
]

if HAS_MATMUL:
    DUNDER_METHODS_FOR_OPERATORS.append(
        ('matmul', '@',),
    )


def internal_name(name):
    return (
        name.startswith('_self_') or
        name == '__wrapped__' or name.startswith('__')
    )


class BaseTracker(object):
    def __init__(self, wrapped, name, data):
        self.__wrapped__ = wrapped
        self._self_name = name
        self._self_data = data
        self._self_is_ordered = True

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)

    def __getattribute__(self, name):
        if internal_name(name):
            return object.__getattribute__(self, name)
        return getattr(self.__wrapped__, name)

    def __setattr__(self, name, value):
        if internal_name(name):
            return object.__setattr__(self, name, value)
        return setattr(self.__wrapped__, name, value)

    def __delattr__(self, name):
        if internal_name(name):
            return object.__delattr__(self, name)

        return getattr(self.__wrapped__, name)

    def __lt__(self, other):
        result = self.__wrapped__ < unwrap(other)
        if not isinstance(result, bool):
            return result
        record(self, '<', result)
        return result

    def __gt__(self, other):
        result = self.__wrapped__ > unwrap(other)
        if not isinstance(result, bool):
            return result
        record(self, '>', result)
        return result

    def __le__(self, other):
        result = self.__wrapped__ <= unwrap(other)
        if not isinstance(result, bool):
            return result
        record(self, '>', not result)
        return result

    def __ge__(self, other):
        result = self.__wrapped__ >= unwrap(other)
        if not isinstance(result, bool):
            return result
        record(self, '<', not result)
        return result

    def __eq__(self, other):
        result = self.__wrapped__ == unwrap(other)
        if not isinstance(result, bool):
            return result
        if result:
            record(self, '<', False)
            record(self, '>', False)
        elif self._self_is_ordered:
            try:
                lt = self < unwrap(other)
            except TypeError:
                self._self_is_ordered = False
            else:
                record(self, '<', lt)
                record(self, '>', not lt)
        return result

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.__wrapped__)


TRACKER_CLASS_CACHE = WeakKeyDictionary()


def tracker_class(typ):
    try:
        return TRACKER_CLASS_CACHE[typ]
    except KeyError:
        pass

    class ProxiedDunders(object):
        for name in dir(typ):
            if name in (
                '__new__', '__slots__', '__subclasshook__',
                '__init_subclass__',
            ):
                continue

            if (
                name.startswith("__") and
                name.endswith("__")
            ):
                try:
                    args = ', '.join(
                        getfullargspec(getattr(typ, name)).args[1:])
                except TypeError:
                    exec(DUNDER_PROPERTY % {'name': name},)
                else:
                    exec(DUNDER_METHOD % {'method': name, 'args': args})

    for k in dir(ProxiedDunders):
        if not k.startswith("__"):
            delattr(ProxiedDunders, k)

    class Tracker(BaseTracker, ProxiedDunders):
        @property
        def __class__(self):
            return typ

        @property
        def __bytes__(self):
            return bytes(self.__wrapped__)

    TRACKER_CLASS_CACHE[typ] = Tracker
    return Tracker


def tracker(wrapped, name, data):
    return tracker_class(type(wrapped))(wrapped, name, data)
