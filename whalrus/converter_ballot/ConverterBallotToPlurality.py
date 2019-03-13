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
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.converter_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from whalrus.ballot.Ballot import Ballot
from whalrus.ballot.BallotPlurality import BallotPlurality
from whalrus.ballot.BallotVeto import BallotVeto
from whalrus.ballot.BallotOneName import BallotOneName
from whalrus.ballot.BallotOrder import BallotOrder
from whalrus.priority.Priority import Priority


class ConverterBallotToPlurality(ConverterBallot):
    """
    Default converter to plurality ballot.

    :param order_priority: option passed to :meth:`BallotOrder.first`.
    :param plurality_priority: option passed to :meth:`BallotPlurality.first`.
    :param veto_priority: option passed to :meth:`BallotVeto.first`.
    :param one_name_priority: option passed to :meth:`BallotOneName.first`.

    This is a default converter to a plurality ballot. It tries to infer the type of input and converts it to
    a plurality ballot.

    Typical usages:

    >>> converter = ConverterBallotToPlurality()
    >>> converter(BallotOneName('a', candidates={'a', 'b'}))
    BallotPlurality('a', candidates={'a', 'b'})
    >>> converter(BallotVeto('a', candidates={'a', 'b'}))
    BallotPlurality('b', candidates={'a', 'b'})
    >>> converter({'a': 10, 'b': 7, 'c':0})
    BallotPlurality('a', candidates={'a', 'b', 'c'})
    >>> converter('a > b ~ c')
    BallotPlurality('a', candidates={'a', 'b', 'c'})
    >>> converter(['a', {'b', 'c'}])
    BallotPlurality('a', candidates={'a', 'b', 'c'})

    Use options for the restrictions:

    >>> converter = ConverterBallotToPlurality(order_priority=Priority.ASCENDING)
    >>> converter(BallotOrder('a ~ b > c'))
    BallotPlurality('a', candidates={'a', 'b', 'c'})
    """

    def __init__(self,
                 order_priority: Priority = Priority.UNAMBIGUOUS,
                 plurality_priority: Priority = Priority.UNAMBIGUOUS,
                 veto_priority: Priority = Priority.UNAMBIGUOUS,
                 one_name_priority: Priority = Priority.UNAMBIGUOUS):
        self.order_priority = order_priority
        self.plurality_priority = plurality_priority
        self.veto_priority = veto_priority
        self.one_name_priority = one_name_priority

    def __call__(self, x: object, candidates: set = None) -> BallotPlurality:
        x = ConverterBallotGeneral()(x, candidates=None)
        if isinstance(x, BallotPlurality):
            return x.restrict(candidates=candidates, priority=self.plurality_priority)
        if isinstance(x, BallotVeto):
            first = x.first(candidates=candidates, priority=self.veto_priority)
            if candidates is None:
                candidates = x.candidates
            else:
                candidates = x.candidates & candidates
            return BallotPlurality(first, candidates=candidates)
        if isinstance(x, BallotOneName):
            x = BallotPlurality(x.candidate, candidates=x.candidates)
            return x.restrict(candidates=candidates, priority=self.one_name_priority)
        if isinstance(x, BallotOrder):
            x = x.restrict(candidates=candidates)
            return BallotPlurality(x.first(priority=self.order_priority), candidates=x.candidates)
        if isinstance(x, Ballot):
            x = ConverterBallotGeneral()(x, candidates=candidates)
            return BallotPlurality(x.first(), candidates=x.candidates)
