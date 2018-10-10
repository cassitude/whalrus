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
import numbers
from typing import KeysView, ValuesView, ItemsView
from whalrus.ballots.BallotOrder import BallotOrder
from whalrus.scales.Scale import Scale
from whalrus.scales.ScaleRange import ScaleRange
from whalrus.scales.ScaleInterval import ScaleInterval
from whalrus.scales.ScaleFromList import ScaleFromList
from whalrus.scales.ScaleFromSet import ScaleFromSet
from whalrus.utils.Utils import cached_property, set_to_str, dict_to_str, dict_to_items


class BallotLevels(BallotOrder):
    """
    Ballot with an evaluation of candidates.

    :param b: a dictionary whose keys are candidates and whose values represent some form of evaluation. The keys and
        the values must be hashable.
    :param candidates: the candidates that were available at the moment when the voter cast her ballot. Default:
        candidates that are explicitly mentioned in the ballot.
    :param scale: a Scale object, representing the authorized scale at the moment when the voter cast her ballot.
        If not specified, Whalrus tries to infer it.

    Most general syntax:
    >>> BallotLevels({'a': 10, 'b': 7, 'c': 3}, candidates={'a', 'b', 'c', 'd', 'e'}, scale=ScaleRange(low=0, high=10))
    BallotLevels({'a': 10, 'b': 7, 'c': 3}, candidates={'a', 'b', 'c', 'd', 'e'}, scale=ScaleRange(low=0, high=10))

    Other examples of syntax:
    >>> BallotLevels({'a': 10, 'b': 7, 'c': 3})
    BallotLevels({'a': 10, 'b': 7, 'c': 3}, candidates={'a', 'b', 'c'}, scale=ScaleRange(low=3, high=10))
    >>> ballot = BallotLevels({'a': 'Good', 'b': 'Bad', 'c': 'Bad'}, scale=ScaleFromList(['Bad', 'Medium', 'Good']))
    >>> ballot.as_weak_order == [{'a'}, {'b', 'c'}]
    True
    """

    # Core features: ballot and candidates
    # ====================================

    def __init__(self, b: dict, candidates: set=None, scale: Scale=None):
        self._input_scale = scale
        super().__init__(b, candidates)

    def _parse(self, b: dict) -> None:
        """
        For this subclass, the internal representation is of the form {'a': 10, 'b': 7, 'c': 3}, meaning
        that a has evaluation 10; b, 7; and c, 3.

        :param b: a dictionary.
        :return: the dictionary itself.
        """
        self._internal_representation = b

    @cached_property
    def as_dict(self) -> dict:
        """
        Evaluation format.

        :return: a dictionary whose keys are candidates and values are evaluations.

        >>> BallotLevels({'a': 10, 'b': 7, 'c': 3}).as_dict == {'a': 10, 'b': 7, 'c': 3}
        True
        """
        return self._internal_representation

    @cached_property
    def as_weak_order(self) -> list:
        return [{k for k in self.as_dict.keys() if self.as_dict[k] == v}
                for v in sorted(set(self.as_dict.values()), reverse=True)]

    @cached_property
    def candidates_in_b(self) -> set:
        return set(self.as_dict.keys())

    @cached_property
    def scale(self) -> Scale:
        """
        The scale.

        :return: a Scale object, representing the authorized scale at the moment when the voter cast her ballot. If
            the scale was not explicitly given, try to infer the scale from the ballot.

        >>> BallotLevels({'a': 10, 'b': 7, 'c': 3}).scale
        ScaleRange(low=3, high=10)
        """
        if self._input_scale is None:
            if len(self) == 0:
                return ScaleFromSet(set())
            if all([isinstance(v, int) for v in self.as_dict.values()]):
                return ScaleRange(low=min(self.as_dict.values()), high=max(self.as_dict.values()))
            if all([isinstance(v, numbers.Number) for v in self.as_dict.values()]):
                return ScaleInterval(low=min(self.as_dict.values()), high=max(self.as_dict.values()))
            return ScaleFromSet(set(self.as_dict.values()))
        return self._input_scale

    # Representation
    # ==============

    def __repr__(self) -> str:
        return 'BallotLevels(%s, candidates=%s, scale=%s)' % (
            dict_to_str(self.as_dict), set_to_str(self.candidates), repr(self.scale)
        )

    def __str__(self) -> str:
        return ', '.join([str(k) + ': ' + str(v) for k, v in dict_to_items(self.as_dict)])

    # Restrict the ballot
    # ===================

    def restrict(self, candidates: set=None, **kwargs) -> 'BallotLevels':
        if kwargs:
            raise TypeError("restrict() got an unexpected keyword argument %r" % list(kwargs.keys())[0])
        if candidates is None:
            return self
        return BallotLevels({k: v for k, v in self.as_dict.items() if k in candidates},
                            candidates=self.candidates & candidates, scale=self.scale)

    # Dictionary behavior
    # ===================

    def __getitem__(self, item: object) -> object:
        """
        Get an evaluation.

        :param item: a candidate.
        :return: the evaluation for this candidate.

        >>> ballot = BallotLevels({'a': 10, 'b': 7, 'c': 3})
        >>> ballot['a']
        10
        """
        return self.as_dict[item]

    def keys(self) -> KeysView:
        """
        Keys of the ballot.

        :return: self.as_dict.keys().
        """
        return self.as_dict.keys()

    def values(self) -> ValuesView:
        """
        Values of the ballot.

        :return: self.as_dict.values().
        """
        return self.as_dict.values()

    def items(self) -> ItemsView:
        """
        Items of the ballot.

        :return: self.as_dict.items().
        """
        return self.as_dict.items()
