from rns import *

bit_len_limbs = 64
overflow_bit_len_limbs = 80
number_of_limbs = 4
crt_modulus_bit_len = bit_len_limbs * number_of_limbs

p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
r = 0x40000000000000000000000000000000224698fc0994a8dd8c46eb2100000001
rns = RNS.setup2(p, r, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)

from random import randint

overflow = 110


def max():
    return (1 << overflow) - 1


def rand():
    return randint(0, 1 << overflow)
