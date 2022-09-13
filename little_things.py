from .my_solver import MySolver
from typing import List
from z3 import If, Or
import z3

# So we can create unique variable names
min_max_id = 0

def Min(s: MySolver, *nums: List[z3.ArithRef]) -> z3.ArithRef:
    assert len(nums) > 0, "Min called with zero arguments. That makes no sense."
    global min_max_id
    if len(nums) == 1:
        return nums[0]
    if len(nums) == 2:
        # Special case because that's probably more efficient
        return If(nums[0] <= nums[1], nums[0], nums[1])
    else:
        # General case
        res = s.Real(f"min{min_max_id}")
        min_max_id += 1
        for n in nums:
            s.add(res <= n)
        s.add(Or(*[res == n for n in nums]))
        return res

def Max(s: MySolver, *nums: List[z3.ArithRef]) -> z3.ArithRef:
    assert len(nums) > 0, "Min called with zero arguments. That makes no sense."
    global min_max_id
    if len(nums) == 1:
        return nums[0]
    if len(nums) == 2:
        # Special case because that's probably more efficient
        return If(nums[0] >= nums[1], nums[0], nums[1])
    else:
        # General case
        res = s.Real(f"max{min_max_id}")
        min_max_id += 1
        for n in nums:
            s.add(res >= n)
        s.add(Or(*[res == n for n in nums]))
        return res
