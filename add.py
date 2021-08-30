from rns import *

crt_modulus_bit_len = 32
bit_len_modulus = 31
bit_len_limbs = 8
number_of_limbs = 4

u0_bit_len = {}
u1_bit_len = {}
for z in range(100):

    rns = RNS.setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
    p = rns.wrong_modulus

    a = rns.rand_int()
    b = rns.rand_int()
    c = a + b
    assert c.value() % p == (a.value() + b.value()) % p
