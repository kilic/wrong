from typing import overload
from rns import *

bit_len_limbs = 68
number_of_limbs = 4
crt_modulus_bit_len = bit_len_limbs * number_of_limbs

wrong_modulus = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
native_modulus = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001
rns = RNS.setup2(wrong_modulus, native_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)

from random import randint

overflow = 110


def max():
    return (1 << overflow) - 1


def rand():
    return randint(0, 1 << overflow)
