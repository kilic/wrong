from random import randint
from rns import *

bit_len_limbs = 64
number_of_limbs = 4
crt_modulus_bit_len = bit_len_limbs * number_of_limbs

wrong_modulus = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
native_modulus = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001
rns = RNS.setup(wrong_modulus, native_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)

analyse(rns)
