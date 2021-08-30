from rns import *

crt_modulus_bit_len = 32
bit_len_modulus = 31
bit_len_limbs = 8
number_of_limbs = 4

u0_bit_len = {}
u1_bit_len = {}
for z in range(1000):

    rns = RNS.setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
    p = rns.wrong_modulus
    T = rns.T

    a = rns.rand_int()
    b = rns.rand_int()
    c = a + b
    assert c.value() % p == (a.value() + b.value()) % p

    acc = rns.rand_int()

    while acc.value() < T:
        acc = acc + rns.rand_int()
    acc = acc + rns.rand_int()    # one more

    r0 = acc.value() % p

    r1, _, _, _, _ = acc.reduce()

    assert r0 == r1.value()
