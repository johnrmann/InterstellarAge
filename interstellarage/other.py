"""
InterstellarAge
other.py

Defines miscelaneous constants and functions.
"""

def int_to_roman(input):
    """
    Given an integer, this function returns a `str` of that integer written
    with Roman numerals.
    """
    
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""
    for a in range(len(ints)):
        count = int(input / ints[i])
        result += nums[i] * count
        input -= ints[i] * count
    return result
