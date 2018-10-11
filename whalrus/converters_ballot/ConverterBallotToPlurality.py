from whalrus.converters_ballot.ConverterBallot import ConverterBallot
from whalrus.converters_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from whalrus.ballots.Ballot import Ballot
from whalrus.ballots.BallotPlurality import BallotPlurality
from whalrus.ballots.BallotVeto import BallotVeto
from whalrus.ballots.BallotOneName import BallotOneName
from whalrus.ballots.BallotOrder import BallotOrder
from whalrus.priority.Priority import Priority


# noinspection PyUnresolvedReferences
class ConverterBallotToPlurality(ConverterBallot):
    """
    Default converter to plurality ballot.

    :param order_priority: option passed to :meth:`BallotOrder.first`.
    :param veto_priority: option passed to :meth:`BallotVeto.first`.

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

    >>> converter = ConverterBallotToPlurality(order_priority=Priority.ASCENDING,
    ...                                        veto_priority=Priority.ASCENDING)
    >>> converter(BallotOrder('a ~ b > c'))
    BallotPlurality('a', candidates={'a', 'b', 'c'})
    >>> converter(BallotVeto('a', candidates={'a', 'b', 'c'}))
    BallotPlurality('b', candidates={'a', 'b', 'c'})
    """

    def __init__(self, order_priority=Priority.UNAMBIGUOUS, veto_priority=Priority.UNAMBIGUOUS,
                 one_name_priority=Priority.UNAMBIGUOUS, plurality_priority=Priority.UNAMBIGUOUS):
        self.veto_priority = veto_priority
        self.order_priority = order_priority
        self.one_name_priority = one_name_priority
        self.plurality_priority = plurality_priority

    def __call__(self, x, candidates=None):
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