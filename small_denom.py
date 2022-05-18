''' Produce solutions with small denominators '''

from fractions import Fraction
import math
from typing import Set, Optional
from z3 import If, Or, Real

from .binary_search import BinarySearch
from .cache import ModelDict, model_to_dict
from .my_solver import MySolver

def find_small_denom_soln(s: MySolver,
                          max_denom: int,
                          target_vars: Optional[Set[str]] = None
                          ) -> Optional[ModelDict]:
    '''Find a solution that tries to maximize the number of variables that have a
    demoninator smaller than `max_denom`. If target_vars is not None, focusses
    only on making the given variables (specified by their name) have a small
    denominator.

    '''

    sat = str(s.check())
    if sat != "sat":
        return None

    m = model_to_dict(s.model())

    # Isolate the constraints this function adds from the outside.
    s.push()

    best_m = m
    best_obj = 0

    # Number of variables that newly have a small denominator
    objective = 0
    max_objective = 0
    old_obj = 0
    for vname in m:
        if target_vars is not None and vname not in target_vars:
            continue
        if type(m[vname]) is Fraction:
            val = m[vname]
            # Fractions just above and below the value
            num = math.ceil(Fraction(val.numerator * max_denom,
                                     val.denominator))
            hi = Fraction(num, max_denom)
            lo = Fraction(num - 1, max_denom)
            assert lo <= val and val <= hi, f"Error in computing hi={hi} and lo={lo} for {val}"

            s.add(Or(
                Real(vname) == val, Real(vname) == lo, Real(vname) == hi))

            if val.denominator > max_denom:
                max_objective += 1
                objective += If(Real(vname) == val, 0, 1)
            else:
                old_obj += 1
        else:
            if target_vars is not None:
                print(f"Warning: {vname} present in `target_vars`, but its type is {type(m[vname])}, not Fraction")


    search = BinarySearch(0, max_objective, 1)
    while True:
        pt = search.next_pt()
        if pt is None:
            break

        # Round to integer
        pt_int = round(pt)

        s.push()
        s.add(objective >= pt_int)
        sat = str(s.check())

        if sat == "sat":
            search.register_pt(pt, 1)
            if pt_int > best_obj:
                best_m = model_to_dict(s.model())
                best_obj = pt_int

        elif sat == "unknown":
            search.register_pt(pt, 2)
        else:
            assert sat == "unsat", f"Unknown value: {sat}"
            search.register_pt(pt, 3)

        s.pop()

    search.get_bounds()

    new_obj = 0
    for vname in best_m:
        if (type(best_m[vname]) is Fraction and
            (target_vars is None or vname in target_vars)):
            val = best_m[vname]
            if val.denominator <= max_denom:
                new_obj += 1
    print(f"Improved number of small numbers from {old_obj} to {new_obj} out of a max of {old_obj + max_objective}")

    # Remove all constraints we added
    s.pop()
    return best_m
