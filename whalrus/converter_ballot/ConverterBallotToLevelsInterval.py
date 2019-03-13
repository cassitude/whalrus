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
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.converter_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from whalrus.ballot.BallotVeto import BallotVeto
from whalrus.ballot.BallotPlurality import BallotPlurality
from whalrus.ballot.BallotOneName import BallotOneName
from whalrus.ballot.BallotLevels import BallotLevels
from whalrus.ballot.BallotOrder import BallotOrder
from whalrus.scale.Scale import Scale
from whalrus.scale.ScaleInterval import ScaleInterval
from whalrus.scale.ScaleFromList import ScaleFromList
from whalrus.scale.ScaleFromSet import ScaleFromSet
from whalrus.scale.ScaleRange import ScaleRange


class ConverterBallotToLevelsInterval(ConverterBallot):
    """
    Default converter to an ``interval'' ballot (suitable for Range Voting).

    :param scale: a :class:`ScaleInterval`.
    :param borda_unordered_give_points: when converting a :class:`BallotOrder`, we use Borda scores (normalized
        to the interval ``[low, high]``). This parameter decides whether unordered candidates of the ballot
        give points to ordered candidates. Cf. meth:`BallotOrder.borda`.

    This is a default converter to an interval ballot. It tries to infer the type of input and converts it to
    a :class:`BallotLevels`, where the scale is of class :class:`ScaleInterval`.

    Typical usages:

    >>> converter = ConverterBallotToLevelsInterval()
    >>> converter(BallotLevels({'a': 1., 'b': 0.5}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(-1., 1.)))
    BallotLevels({'a': 1.0, 'b': 0.75}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotLevels({'a': 5, 'b': 4}, candidates={'a', 'b', 'c'}, scale=ScaleRange(0, 5)))
    BallotLevels({'a': 1.0, 'b': 0.8}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotLevels({'a': 3, 'b': 0}, candidates={'a', 'b', 'c'}, scale=ScaleFromSet({-1, 0, 3})))
    BallotLevels({'a': 1.0, 'b': 0.25}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotLevels({'a': 'Excellent', 'b': 'Very Good'}, candidates={'a', 'b', 'c'},
    ...                        scale=ScaleFromList(['Bad', 'Medium', 'Good', 'Very Good', 'Excellent'])))
    BallotLevels({'a': 1.0, 'b': 0.75}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotOneName('a', candidates={'a', 'b', 'c'}))
    BallotLevels({'a': 1.0, 'b': 0.0, 'c': 0.0}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotPlurality('a', candidates={'a', 'b', 'c'}))
    BallotLevels({'a': 1.0, 'b': 0.0, 'c': 0.0}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter(BallotVeto('a', candidates={'a', 'b', 'c'}))
    BallotLevels({'a': 0.0, 'b': 1.0, 'c': 1.0}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter('a > b > c')
    BallotLevels({'a': 1.0, 'b': 0.5, 'c': 0.0}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(low=0.0, high=1.0))

    Options for converting ordered ballots:

    >>> converter = ConverterBallotToLevelsInterval(borda_unordered_give_points=False)
    >>> converter(BallotOrder('a > b > c', candidates={'a', 'b', 'c', 'd', 'e'}))  #doctest: +ELLIPSIS
    BallotLevels({'a': 1.0, 'b': 0.5, 'c': 0.0}, candidates={'a', ..., 'e'}, scale=ScaleInterval(low=0.0, high=1.0))
    >>> converter = ConverterBallotToLevelsInterval(borda_unordered_give_points=True)
    >>> converter(BallotOrder('a > b > c', candidates={'a', 'b', 'c', 'd', 'e'}))  #doctest: +ELLIPSIS
    BallotLevels({'a': 1.0, 'b': 0.75, 'c': 0.5}, candidates={'a', ..., 'e'}, scale=ScaleInterval(low=0.0, high=1.0))
    """

    def __init__(self, scale: Scale = ScaleInterval(0., 1.), borda_unordered_give_points: bool = True):
        self.scale = scale
        self.low = scale.low
        self.high = scale.high
        self.borda_unordered_give_points = borda_unordered_give_points

    def __call__(self, x: object, candidates: set=None) -> BallotLevels:
        x = ConverterBallotGeneral()(x, candidates=None)
        if isinstance(x, BallotVeto):
            if x.candidate is None:
                return BallotLevels(dict(), candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
            return BallotLevels({c: self.low if c == x.candidate else self.high for c in x.candidates},
                                candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
        if isinstance(x, BallotOneName):  # Including Plurality
            if x.candidate is None:
                return BallotLevels(dict(), candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
            return BallotLevels({c: self.high if c == x.candidate else self.low for c in x.candidates},
                                candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
        if isinstance(x, BallotLevels):
            if not x.scale.is_bounded:
                if all([isinstance(v, numbers.Number) for v in x.values()]):
                    x_min, x_max = min(x.values()), max(x.values())
                    if x_min >= self.low and x_max <= self.high:
                        return BallotLevels(
                            x.as_dict, candidates=x.candidates,
                            scale=ScaleInterval(low=self.low, high=self.high)).restrict(candidates=candidates)
                    else:
                        x = BallotLevels(x.as_dict, candidates=x.candidates,
                                         scale=ScaleInterval(low=min(x.values()), high=max(x.values())))
                else:
                    x = BallotLevels(x.as_dict, candidates=x.candidates, scale=ScaleFromSet(set(x.values())))
            try:  # Interpret as a cardinal ballot
                return BallotLevels(
                    {c: self.low + (self.high - self.low) * (v - x.scale.low) / (x.scale.high - x.scale.low)
                     for c, v in x.items()},
                    candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
            except (TypeError, AttributeError):
                x_scale = x.scale
                if isinstance(x_scale, ScaleFromList):
                    return BallotLevels(
                        {c: self.low + (self.high - self.low) * x_scale.as_dict[x[c]] / (len(x_scale.levels) - 1)
                         for c, v in x.items()},
                        candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
        if isinstance(x, BallotOrder):
            borda = x.borda(unordered_give_points=self.borda_unordered_give_points)
            score_max = len(x.candidates) - 1 if self.borda_unordered_give_points else len(x.candidates_in_b) - 1
            return BallotLevels(
                {c: self.low + (self.high - self.low) * borda[c] / score_max for c in x.candidates_in_b},
                candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
        raise NotImplementedError
