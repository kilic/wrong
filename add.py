from rns import *
from setup import rand_rns

crt_modulus_bit_len = 32

u0_bit_len = {}
u1_bit_len = {}

for i in range(1000):
    modulus_offset = 1
    rns = rand_rns(crt_modulus_bit_len, modulus_offset)
    p = rns.wrong_modulus
    T = rns.T

    a = rns.rand_in_max()
    b = rns.rand_in_max()
    c = a + b
    assert c.value() % p == (a.value() + b.value()) % p
