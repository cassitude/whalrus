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
from whalrus.utils.Utils import cached_property
from whalrus.rule.Rule import Rule
from whalrus.rule.RuleCondorcet import RuleCondorcet
from whalrus.rule.RuleBorda import RuleBorda
from whalrus.rule.RuleSequentialTieBreak import RuleSequentialTieBreak
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.priority.Priority import Priority
from typing import Union


class RuleBlack(RuleSequentialTieBreak):
    """
    Black's rule.

    :param rule_condorcet: a Rule. Used as the main victory criterion. Default: :class:`RuleCondorcet`.
    :param rule_borda: a Rule. Used as the secondary victory criterion. Default: :class:`RuleBorda`.

    The Condorcet winner is elected, even if it does not have the best Borda score:

    >>> rule = RuleBlack(ballots=['a > b > c', 'b > c > a'], weights=[6, 4])
    >>> rule.rule_condorcet_.matrix_majority_.matrix_weighted_majority_.as_array_
    array([[0. , 0.6, 0.6],
           [0.4, 0. , 1. ],
           [0.4, 0. , 0. ]])
    >>> rule.order_
    [{'a'}, {'b'}, {'c'}]

    When there is no Condorcet winner, candidates are sorted according to their Borda scores:

    >>> rule = RuleBlack(ballots=['a > b > c', 'b > c > a', 'c > a > b'], weights=[2, 1, 1])
    >>> rule.rule_condorcet_.matrix_majority_.matrix_weighted_majority_.as_array_
    array([[0.  , 0.75, 0.5 ],
           [0.25, 0.  , 0.75],
           [0.5 , 0.25, 0.  ]])
    >>> rule.order_
    [{'a'}, {'b'}, {'c'}]
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, converter: ConverterBallot = None,
                 rule_condorcet: Rule = None, rule_borda: Rule = None):
        if rule_condorcet is None:
            rule_condorcet = RuleCondorcet()
        self.rule_condorcet = rule_condorcet
        if rule_borda is None:
            rule_borda = RuleBorda()
        self.rule_borda = rule_borda
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates,
            tie_break=tie_break, converter=converter,
            rules=[rule_condorcet, rule_borda]
        )

    @cached_property
    def rule_condorcet_(self):
        """
        The Condorcet rule.

        :return: the Condorcet rule (once computed on the profile).
        """
        return self.rule_condorcet(self.profile_converted_)

    @cached_property
    def rule_borda_(self):
        """
        The Borda rule.

        :return: the Borda rule (once computed on the profile).
        """
        return self.rule_borda(self.profile_converted_)
