# -*- coding: utf-8 -*-
"""
Copyright Sylvain Bouveret, Yann Chevaleyre and François Durand
sylvain.bouveret@imag.fr, yann.chevaleyre@dauphine.fr, fradurand@gmail.com

This file is part of Whalrus.

Whalrus is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Whalrus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Whalrus.  If not, see <http://www.gnu.org/licenses/>.
"""
from whalrus.scale.Scale import Scale
from typing import Iterable


class ScaleInterval(Scale):
    """
    A scale given by an interval of floats.

    :param low: lowest float.
    :param high: highest float.

    >>> ScaleInterval(low=0., high=10.)
    ScaleInterval(low=0.0, high=10.0)
    """

    def __init__(self, low: float = 0., high: float = 1.):
        self._low = low
        self._high = high

    @property
    def low(self) -> object:
        return self._low

    @property
    def high(self) -> object:
        return self._high

    @property
    def is_bounded(self) -> bool:
        return True

    def __repr__(self):
        return 'ScaleInterval(low=%s, high=%s)' % (self.low, self.high)

    # Min, max and sort
    # -----------------

    def min(self, iterable: Iterable) -> object:
        return min(iterable)

    def max(self, iterable: Iterable) -> object:
        return max(iterable)

    # noinspection PyMethodMayBeStatic
    def sort(self, some_list: list) -> None:
        some_list.sort()

    def argsort(self, some_list: list) -> list:
        return sorted(range(len(some_list)), key=lambda i: some_list[i])
