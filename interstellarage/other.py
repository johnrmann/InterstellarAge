"""
InterstellarAge
other.py

Defines miscelaneous constants and functions.
"""

def coinflip(p):
    """
    Simulates a biased coin that yields heads with probability `p` (`float`).
    """
    
    import random
    return random.random() <= p



def int_to_roman(input):
    """
    Given an integer, this function returns a `str` of that integer written
    with Roman numerals.
    """
    
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""
    for a in range(len(ints)):
        count = int(input / ints[a])
        result += nums[a] * count
        input -= ints[a] * count
    return result



def irange(n, k):
    """
    Inclusive range.
    """

    return range(n, k+1)



def rand_float_range(a, b):
    import random

    d = b - a
    dice = random.random()
    result = d * dice
    result += a
    return result
