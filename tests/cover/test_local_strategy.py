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

from hypothesis import given
import hypothesis.strategies as st


def test_local_strategy_definition_with_draw():
    @st.local
    def rectangle_lists(data):
        size = data.draw(st.integers(0, 5))
        return data.draw(
            st.lists(
                st.lists(st.booleans(), min_size=size, max_size=size),
                min_size=1
            )
        )

    @given(rectangle_lists)
    def test(r):
        assert len(set(map(len, r))) == 1

    test()


def test_local_strategy_definition_with_call():
    @given(st.local(lambda data: data(st.lists(max_size=data(st.just(0))))))
    def test(r):
        assert len(r) == 0

    test()
