#!/usr/bin/env python3

import math

def atk_strat_equal_bias_atk(x):
    return math.floor( x / 2 ), x - math.floor( x / 2 )

def atk_strat_equal_bias_def(x):
    return math.ceil( x / 2 ), x - math.ceil( x / 2 )

def dmg_strat_all_attr1(n, attr1, attr2):
    return n, 0

def dmg_strat_all_attr2(n, attr1, attr2):
    return 0, n

def dmg_strat_all_attr2_sensible(n, attr1, attr2):
    d1 = 0
    d2 = n
    if((attr2-1) < n):
        d1 = d1 + (n - (attr2-1))
    return d1, n - d1

def dmg_strat_equal_bias_attr1(n, attr1, attr2):
    return math.floor( n / 2 ). n - math.floor( n / 2 )

def dmg_strat_equal_bias_attr2(n, attr1, attr2):
    return math.ceil( n / 2 ), n - math.ceil( n / 2 )

def dmg_strat_equal_bias_attr2_sensible(n, attr1, attr2):
    d1 = math.floor( n / 2 )
    d2 = n - d1
    if(attr2 - 1 < d2):
        d1 += d2 - (attr2-1)
    return min(d1, n), n - min(d1, n)

