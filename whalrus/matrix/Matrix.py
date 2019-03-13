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
import numpy as np
from whalrus.utils.Utils import DeleteCacheMixin, cached_property, NiceSet, set_to_list, NiceDict
from whalrus.converter_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from typing import Union


class Matrix(DeleteCacheMixin):
    """
    A way to compute a matrix from a profile.

    :param ballots: if mentioned, will be passed to `__call__` immediately after initialization.
    :param weights: if mentioned, will be passed to `__call__` immediately after initialization.
    :param voters: if mentioned, will be passed to `__call__` immediately after initialization.
    :param candidates: if mentioned, will be passed to `__call__` immediately after initialization.
    :param converter: the converter that is used to convert input ballots. Default: :class:`ConverterBallotGeneral`.

    A :class:`Matrix` object is a callable whose inputs are ballots and optionally weights, voters and candidates. When
    it is called, it loads the profile. The output of the call is the :class:`Matrix` object itself.
    But after the call, you can access to the computed variables (ending with an underscore), such as
    :attr:`as_dict_` or :attr:`as_df_`.

    Cf. :class:`MatrixWeightedMajority` for some examples.
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 converter: ConverterBallot = None):
        """
        Remark: this `__init__` must always be called at the end of the subclasses' `__init__`.
        """
        # Parameters
        if converter is None:
            converter = ConverterBallotGeneral()
        self.converter = converter
        # Computed variables
        self.profile_ = None
        self.profile_converted_ = None
        self.candidates_ = None
        # Optional: load a profile at initialization
        if ballots is not None:
            self(ballots=ballots, weights=weights, voters=voters, candidates=candidates)

    def __call__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None):
        self.profile_ = Profile(ballots, weights=weights, voters=voters)
        self.profile_converted_ = Profile([self.converter(b, candidates) for b in self.profile_],
                                          weights=self.profile_.weights, voters=self.profile_.voters)
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
    def as_dict_(self) -> NiceDict:
        """
        The matrix, as a dictionary (more exactly, a :class:`NiceDict`).

        :return: a :class:`NiceDict`. Keys are pairs of candidates, and values are the coefficients of the matrix.
        """
        raise NotImplementedError

    @cached_property
    def candidates_as_list_(self):
        """
        The list of candidates.

        :return: a list. Candidates are sorted if possible.
        """
        return set_to_list(self.candidates_)

    @cached_property
    def as_array_(self) -> np.array:
        """
        The matrix, as a numpy array.

        :return: a numpy array. Each row and each column corresponds to a candidate (in the order of
            :attr:`candidates_as_list_`).
        """
        return np.array([[self.as_dict_[(c, d)] for d in self.candidates_as_list_] for c in self.candidates_as_list_])
