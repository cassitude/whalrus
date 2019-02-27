from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.converter_ballot.ConverterBallotToLevelsRange import ConverterBallotToLevelsRange
from whalrus.ballot.BallotVeto import BallotVeto
from whalrus.ballot.BallotPlurality import BallotPlurality
from whalrus.ballot.BallotOneName import BallotOneName
from whalrus.ballot.BallotLevels import BallotLevels
from whalrus.scale.ScaleInterval import ScaleInterval
from whalrus.scale.ScaleFromList import ScaleFromList
from whalrus.scale.ScaleFromSet import ScaleFromSet
from whalrus.scale.ScaleRange import ScaleRange


class ConverterBallotToLevelsListNonNumeric(ConverterBallot):
    """
    Default converter to a ``level / non-numeric'' ballot (suitable for Majority Judgment).

    :param scale: the scale.
    :param borda_unordered_give_points: when converting a :class:`BallotOrder`, we use Borda scores (normalized
        to the interval ``[low, high]`` and rounded). This parameter decides whether unordered candidates of the ballot
        give points to ordered candidates. Cf. meth:`BallotOrder.borda`.

    This is a default converter to a ballot using non-numeric levels. It tries to infer the type of input and converts
    it to a :class:`BallotLevels`, where the scale is of class :class:`ScaleFromList`. Its functions essentially the
    same as class:`ConverterBallotToLevelsInterval`, but it then maps to non-numeric levels.

    Typical usages:

    >>> converter = ConverterBallotToLevelsListNonNumeric(scale=ScaleFromList([
    ...     'Bad', 'Medium', 'Good', 'Very Good', 'Great', 'Excellent']))
    >>> converter(BallotLevels({'a': 1., 'b': 0.2}, candidates={'a', 'b', 'c'}, scale=ScaleInterval(-1., 1.))).as_dict
    {'a': 'Excellent', 'b': 'Very Good'}
    >>> converter(BallotLevels({'a': 5, 'b': 4}, candidates={'a', 'b', 'c'}, scale=ScaleRange(0, 5))).as_dict
    {'a': 'Excellent', 'b': 'Great'}
    >>> converter(BallotLevels({'a': 4, 'b': 0}, candidates={'a', 'b', 'c'}, scale=ScaleFromSet({-1, 0, 4}))).as_dict
    {'a': 'Excellent', 'b': 'Medium'}
    >>> converter(BallotOneName('a', candidates={'a', 'b', 'c'})).as_dict
    {'a': 'Excellent', 'b': 'Bad', 'c': 'Bad'}
    >>> converter(BallotPlurality('a', candidates={'a', 'b', 'c'})).as_dict
    {'a': 'Excellent', 'b': 'Bad', 'c': 'Bad'}
    >>> converter(BallotVeto('a', candidates={'a', 'b', 'c'})).as_dict
    {'a': 'Bad', 'b': 'Excellent', 'c': 'Excellent'}
    >>> converter('a > b > c > d').as_dict
    {'a': 'Excellent', 'b': 'Very Good', 'c': 'Good', 'd': 'Bad'}
    """

    def __init__(self, scale, borda_unordered_give_points: bool=True):
        self.scale = scale
        self.borda_unordered_give_points = borda_unordered_give_points

    def __call__(self, x: object, candidates: set =None) -> BallotLevels:
        x = ConverterBallotToLevelsRange(
            scale=ScaleRange(low=0, high=len(self.scale.levels) - 1),
            borda_unordered_give_points=self.borda_unordered_give_points
        )(x, candidates=None)
        return BallotLevels({c: self.scale.levels[v] for c, v in x.items()},
                            candidates=x.candidates, scale=self.scale).restrict(candidates=candidates)
