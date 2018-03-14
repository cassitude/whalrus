
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

class Profile(dict):
    pass

    def __init__(self,votes,weights=None,candidates=None):
        if isinstance(votes,list):
            votes = dict(enumerate(votes))
        
        if isinstance(votes,dict):
            super().__init__(votes)
        elif isinstance(votes,list):
            super().__init__( dict(enumerate(votes)) )
        pass
    #    if candidates is None:
    #        candidates = ...
    ##        candidates = ...
     #   pass
    def candidates(self):
        pass


