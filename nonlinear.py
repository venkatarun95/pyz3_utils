from .my_solver import MySolver
from typing import List, Optional, Tuple, Union
import z3
from z3 import And, ArithRef, BoolRef, If, Implies, Not, Sum


class Piecewise:
    '''
    A variable that depends on a list of conditions. E.g. "x = 1 if y < 0 and x
    = 2 otherwise", where x is the variable this class represents.

    It is useful for defining multiplications for instance. The given
    conditions *must* be mutually exclusive and exhaustive. This can be
    verified through a separate Z3 query accessible through `verify`

    '''

    # To give unique names to piecewise variables
    id: int = 0
    # IF `val` has already been called
    val_def: Optional[ArithRef]

    def __init__(self, s: MySolver,
                 vals: Union[List[Tuple[BoolRef, float]],
                             List[Tuple[BoolRef, int]]]):
        self.s = s
        self.vals = vals
        self.id = Piecewise.id
        Piecewise.id += 1
        # We may create multiple aux variables distinguished by this
        self.aux_id = 0
        self.val_def = None

    def val(self) -> ArithRef:
        if self.val_def is not None:
            return self.val_def
        self.val_def = self.s.Real(f"auxPiecewiseVal_{self.id}")
        for (c, v) in self.vals:
            self.s.add(Implies(c, self.val_def == v))
        return self.val_def

    def __mul__(self, other: Union[ArithRef, float, int]) -> ArithRef:
        if isinstance(other, float) or isinstance(other, int):
            return self.val() * other

        aux = self.s.Real(f"auxPiecewiseMul_{self.id},{self.aux_id}")
        self.aux_id += 1
        for (c, v) in self.vals:
            self.s.add(Implies(c, aux == v * other))
        return aux

    def __add__(self, other: Union[ArithRef, float, int]) -> ArithRef:
        aux = self.s.Real(f"auxPiecewiseAdd_{self.id},{self.aux_id}")
        self.aux_id += 1
        for (c, v) in self.vals:
            self.s.add(Implies(c, aux == v + other))
        return aux

    def verify(self, s: Optional[MySolver] = None):
        '''Verify that the conditions are mutually exclusive and exhaustive. Takes an
        optional `MySolver` object that can contain additional constraints to
        ensure this is the case.

        '''
        if s is None:
            s = MySolver()

        num_sat = sum([If(c, 1, 0) for (c, _) in self.vals])
        s.add(num_sat != 1)
        s.check()
        satisfiable = s.check()
        assert satisfiable != z3.unsat, f"Unable to check that options are mutually exclusive and exhaustive. Got {satisfiable} for {str(self.vals)}"


def create_linear_piecewise(start: float, end: float, step: float) -> Piecewise:
    '''Construct a `Piecewise` object with linearly spaced pieces'''
    pass
