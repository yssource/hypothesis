# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Most of this work is copyright (C) 2013-2019 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import absolute_import, division, print_function

from hypothesis.searchstrategy.strategies import SampledFromStrategy, is_simple_data


class JustStrategy(SampledFromStrategy):
    """A strategy which always returns a single fixed value.

    It's implemented as a length-one SampledFromStrategy so that all our
    special-case logic for filtering and sets applies also to just(x).
    """

    def __init__(self, value):
        SampledFromStrategy.__init__(self, [value])

    @property
    def value(self):
        return self.elements[0]

    def __repr__(self):
        return "just(%r)" % (self.value,)

    def calc_has_reusable_values(self, recur):
        return True

    def calc_is_cacheable(self, recur):
        return is_simple_data(self.value)

    def do_draw(self, data):
        return self.value
