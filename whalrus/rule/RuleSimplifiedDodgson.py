from whalrus.rule.RuleScoreNum import RuleScoreNum
from whalrus.priority.Priority import Priority
from whalrus.converter_ballot.ConverterBallotToOrder import ConverterBallotToOrder
from whalrus.utils.Utils import cached_property, NiceDict
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.matrix.Matrix import Matrix
from whalrus.matrix.MatrixWeightedMajority import MatrixWeightedMajority
from typing import Union


class RuleSimplifiedDodgson(RuleScoreNum):
    """
    Simplified Dodgson rule.

    :param default_converter: the default is :class:`ConverterBallotToOrder`.
    :param matrix_weighted_majority: a :class:`Matrix`. Default: ``MatrixWeightedMajority(antisymmetric=True)``.

    The score of a candidate is the sum of the negative non-diagonal coefficient on its raw of the matrix.

    >>> rule = RuleSimplifiedDodgson(ballots=['a > b > c', 'b > a > c', 'c > a > b'], weights=[3, 3, 2])
    >>> rule.matrix_weighted_majority_.as_df_
          a     b    c
    a  0.00  0.25  0.5
    b -0.25  0.00  0.5
    c -0.50 -0.50  0.0
    >>> rule.scores_
    {'a': 0, 'b': -0.25, 'c': -1.0}
    >>> rule.winner_
    'a'
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None, converter: ConverterBallot = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, default_converter: ConverterBallot = None,
                 matrix_weighted_majority: Matrix = None):
        if default_converter is None:
            default_converter = ConverterBallotToOrder()
        if matrix_weighted_majority is None:
            matrix_weighted_majority = MatrixWeightedMajority(antisymmetric=True)
        self.matrix_weighted_majority = matrix_weighted_majority
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates, converter=converter,
            tie_break=tie_break, default_converter=default_converter
        )

    @cached_property
    def matrix_weighted_majority_(self):
        """
        The weighted majority matrix.

        :return: the weighted majority matrix (once computed with the given profile).
        """
        return self.matrix_weighted_majority(self.profile_converted_)

    @cached_property
    def scores_(self) -> NiceDict:
        matrix = self.matrix_weighted_majority_
        return NiceDict({c: sum([v for (i, j), v in matrix.as_dict_.items() if i == c and j != c and v < 0])
                         for c in matrix.candidates_})