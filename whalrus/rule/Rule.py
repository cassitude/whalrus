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
import logging
from whalrus.utils.Utils import DeleteCacheMixin, cached_property, NiceSet
from whalrus.priority.Priority import Priority
from whalrus.converter_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from typing import Union


class Rule(DeleteCacheMixin):
    """
    A voting rule.

    :param ballots: if mentioned, will be passed to ``__call__`` immediately after initialization.
    :param weights: if mentioned, will be passed to ``__call__`` immediately after initialization.
    :param voters: if mentioned, will be passed to ``__call__`` immediately after initialization.
    :param candidates: if mentioned, will be passed to ``__call__`` immediately after initialization.
    :param tie_break: a tie-break rule.
    :param converter: the converter that is used to convert input ballots. Default: :class:`ConverterBallotGeneral`.

    A :class:`Rule` object is a callable whose inputs are ballots and optionally weights, voters and candidates.
    When the rule is called, it loads the profile. The output of the call is the rule itself. But
    after the call, you can access to the computed variables (ending with an underscore), such as
    :attr:`cowinners_`.

    At the initialization of a :class:`Rule` object, some options can be given, such as a tie-break rule. In some
    subclasses, there can also be an option about the way to count abstentions, etc.

    Cf. :class:`RulePlurality` for some examples.

    :ivar profile_original\_: the profile as it is entered by the user. This uses the constructor of :class:`Profile`.
        Hence indirectly, it uses :class:`ConverterBallotGeneral` to ensure, for example, that strings like
        ``'a > b > c'`` are converted to :class:`Ballot` objects.
    :ivar profile_converted\_: the profile, with ballots that are adequate for the voting rule. For example,
        in :class:`RulePlurality`, it will be :class:`BallotPlurality` objects, even if the original ballots are
        :class:`BallotOrder` objects.
    :ivar candidates\_: the candidates of the election, as entered in the ``__call__``.
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, converter: ConverterBallot = None):
        """
        Remark: this `__init__` must always be called at the end of the subclasses' `__init__`.
        """
        if converter is None:
            converter = ConverterBallotGeneral()
        # Parameters
        self.tie_break = tie_break
        self.converter = converter
        # Computed variables
        self.profile_original_ = None
        self.profile_converted_ = None
        self.candidates_ = None
        # Optional: load a profile at initialization
        if ballots is not None:
            self(ballots=ballots, weights=weights, voters=voters, candidates=candidates)

    def __call__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None):
        self.profile_original_ = Profile(ballots, weights=weights, voters=voters)
        self.profile_converted_ = Profile([self.converter(b, candidates) for b in self.profile_original_],
                                          weights=self.profile_original_.weights, voters=self.profile_original_.voters)
        if candidates is None:
            candidates = NiceSet(set().union(*[b.candidates for b in self.profile_converted_]))
        self.candidates_ = candidates
        self._check_profile(candidates)
        self.delete_cache()
        return self

    def _check_profile(self, candidates: set) -> None:
        if any([b.candidates != candidates for b in self.profile_converted_]):
            logging.warning('Some ballots do not have the same set of candidates as the whole election.')

    @cached_property
    def n_candidates_(self) -> int:
        """
        Number of candidates.

        :return: the number of candidates.
        """
        return len(self.candidates_)

    @cached_property
    def cowinners_(self) -> NiceSet:
        """
        Cowinners of the election.

        :return: the set of cowinners.
        """
        return self.order_[0]

    @cached_property
    def winner_(self) -> object:
        """
        Winner of the election.

        :return: the winner of the election (which may use a tie-breaking rule).
        """
        return self.tie_break.choice(self.cowinners_)

    @cached_property
    def cotrailers_(self) -> NiceSet:
        """
        "Cotrailers" of the election.

        The candidates that fare worst in the election. For example, in a rule based on a notion of score, it would
        be the candidates that are tied for worst score.

        :return: the set of "cotrailers".
        """
        return self.order_[-1]

    @cached_property
    def trailer_(self) -> object:
        """
        "Trailer" of the election.

        :return: the "trailer" of the election (which may use a tie-breaking rule).
        """
        return self.tie_break.choice(self.cotrailers_, reverse=True)

    @cached_property
    def order_(self) -> list:
        """
        Result of the election as a (weak) order over the candidates.

        :return: a list of sets (or, more exactly, :class:`NiceSet` objects). The first set contains the candidates
            that are tied for victory, etc.
        """
        raise NotImplementedError

    @cached_property
    def strict_order_(self) -> list:
        """
        Result of the election as a strict order over the candidates.

        :return: a list whose first element is the winner, etc (which may use a tie-breaking rule).
        """
        return [candidate for tie_class in self.order_ for candidate in self.tie_break.sort(tie_class)]
