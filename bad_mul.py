from rns import *
from setup import rand_rns

crt_modulus_bit_len = 32
rns = rand_rns(crt_modulus_bit_len, 1)

# a, b = rns.rand_in_max(), rns.rand_in_max()
# a.bad_mul(b)

a, b = rns.rand_in_max(), rns.from_value(0)
a.bad_mul_2(b)
