from typing import List, Tuple
from z3 import And, Implies, Not, Or
import z3

from .my_solver import MySolver

class IfStmt:
    # The compiled x => y pairs of (x, y)
    compiled: List[Tuple[z3.BoolRef, z3.BoolRef]]
    # Conditions so far, so we can implement elif and else
    conds: List[z3.BoolRef]
    # Mark whether Else has been called yet, after which no further things may be called
    done: bool

    def __init__(self, cond: z3.BoolRef, *stmts):
        '''
        Implements a traditional if statement in z3
        '''

        self.compiled = []
        self.conds = [cond]
        self.done = False

        self.__add_stmts(cond, stmts)

    def Elif(self, cond: z3.BoolRef, *stmts):
        '''
        Implements an elif statement in z3
        '''

        if self.done:
            raise Exception("Cannot call Elif after Else")

        self.__add_stmts(And(Not(Or(*self.conds)), cond), stmts)
        self.conds.append(cond)

        # Returns self so we can use the method chaining syntax
        return self

    def Else(self, *stmts):
        '''
        Implements an else statement in z3
        '''

        if self.done:
            raise Exception("Cannot call Else after Else")

        self.__add_stmts(Not(Or(*self.conds)), stmts)
        self.done = True

        # Returns self so we can use the method chaining syntax
        return self

    def add_to_solver(self, s: MySolver):
        '''
        Adds the compiled statements to the solver
        '''

        for (cond, stmt) in self.compiled:
            s.add(Implies(cond, stmt))

    def __add_stmts(self, cond: z3.BoolRef, stmts: List[z3.BoolRef]):
        for stmt in stmts:
            if type(stmt) == IfStmt:
                for (c, s) in stmt.compiled:
                    self.compiled.append(
                        (And(cond, c), s))
            else:
                self.compiled.append((cond, stmt))