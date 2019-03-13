from whalrus.ballot.BallotOrder import BallotOrder
from whalrus.scale.Scale import Scale
from whalrus.utils.Utils import cached_property, NiceDict
from whalrus.scorer.Scorer import Scorer
from typing import Union


class ScorerBucklin(Scorer):
    """
    Scorer for Bucklin's rule.

    :param k: the number of points to distribute. Intuitively: the ``k`` candidates at the highest ranks will receive
        1 point each. In case of tie, some points may be divided between the tied candidates.
    :param unordered_receive_points: whether unordered candidates should receive points.
    :param absent_receive_points: whether absent candidates should receive points.

    Typical usage:

    >>> ScorerBucklin(BallotOrder('a > b > c > d > e'), candidates={'a', 'b', 'c', 'd', 'e'}, k=2).scores_
    {'a': 1.0, 'b': 1.0, 'c': 0.0, 'd': 0.0, 'e': 0.0}

    In the example below, candidates ``a``, ``b`` and ``c`` are `ordered', ``d`` and ``e`` are `unordered',
    and ``f`` and ``g`` are `absent' in the ballot, meaning that they were not even available when the voter cast
    her ballot. By default, we count as if the order was the unordered candidates were below the ordered candidates,
    and the absent candidates even lower.

    >>> ballot = BallotOrder('a > b ~ c', candidates={'a', 'b', 'c', 'd', 'e'})
    >>> candidates_election = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
    >>> ScorerBucklin(ballot, candidates=candidates_election, k=2).scores_
    {'a': 1.0, 'b': 0.5, 'c': 0.5, 'd': 0.0, 'e': 0.0, 'f': 0.0, 'g': 0.0}
    >>> ScorerBucklin(ballot, candidates=candidates_election, k=4).scores_
    {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 0.5, 'e': 0.5, 'f': 0.0, 'g': 0.0}
    >>> ScorerBucklin(ballot, candidates=candidates_election, k=6).scores_
    {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 1.0, 'e': 1.0, 'f': 0.5, 'g': 0.5}

    Using the options, unordered and/or absent candidates can always receive 0 point, or even not be mentioned in the
    score dictionary at all:

    >>> ScorerBucklin(ballot, candidates=candidates_election, k=6,
    ...     unordered_receive_points=False, absent_receive_points=None).scores_
    {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 0.0, 'e': 0.0}
    """

    def __init__(self, ballot: BallotOrder = None, voter: object = None, candidates: set = None,
                 scale: Scale = None,
                 k: int = 1,
                 unordered_receive_points: Union[bool, None] = True, absent_receive_points: Union[bool, None] = True):
        self.k = k
        self.absent_receive_points = absent_receive_points
        self.unordered_receive_points = unordered_receive_points
        super().__init__(ballot=ballot, voter=voter, candidates=candidates, scale=scale)

    @property
    def k(self):
        return self._k

    @k.setter
    def k(self, value):
        self.delete_cache()
        self._k = value

    @cached_property
    def scores_(self) -> NiceDict:
        scores = NiceDict()
        points_remaining = self.k
        # Ordered candidates
        for indifference_class in self.ballot_.as_weak_order[:]:
            n_indifference = len(indifference_class)
            if n_indifference <= points_remaining:
                scores.update({c: 1. for c in indifference_class})
                points_remaining -= n_indifference
            else:
                scores.update({c: points_remaining / n_indifference for c in indifference_class})
                points_remaining = 0.
        # Unordered candidates
        if self.unordered_receive_points is False:
            scores.update({c: 0. for c in self.ballot_.candidates_not_in_b})
        elif self.unordered_receive_points is True:
            unordered = self.ballot_.candidates_not_in_b
            n_unordered = len(unordered)
            if n_unordered <= points_remaining:
                scores.update({c: 1. for c in unordered})
                points_remaining -= n_unordered
            else:
                scores.update({c: points_remaining / n_unordered for c in unordered})
                points_remaining = 0.
        # Absent candidates
        if self.absent_receive_points is False:
            scores.update({c: 0. for c in self.candidates_ - self.ballot_.candidates})
        elif self.absent_receive_points is True:
            absent = self.candidates_ - self.ballot_.candidates
            n_absent = len(absent)
            if n_absent <= points_remaining:
                scores.update({c: 1. for c in absent})
            else:
                scores.update({c: points_remaining / n_absent for c in absent})
        return scores
