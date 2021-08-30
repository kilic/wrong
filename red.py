from rns import *
from random import randint

crt_modulus_bit_len = 32
bit_len_modulus = 28
bit_len_limbs = 8
number_of_limbs = 4

u0_bit_len = {}
u1_bit_len = {}
for z in range(1000):

    rns = RNS.setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
    p = rns.wrong_modulus

    a_val = p - 1
    assert rns.overflow_ratio() > 0
    b = randint(1, rns.overflow_ratio())
    c = randint(0, b - 1)
    a_val = a_val * b
    a = rns.from_value(a_val)

    r, q, t, u0, u1 = a.reduce(c)
    assert r.value() % p == a.value() % p

    _u0 = u0.bit_length()
    _u1 = u1.bit_length()

    if _u0 not in u0_bit_len:
        u0_bit_len[_u0] = 0

    if _u1 not in u1_bit_len:
        u1_bit_len[_u1] = 0

    u0_bit_len[_u0] += 1
    u1_bit_len[_u1] += 1

print("--- u0 bit")

for key in u0_bit_len.keys():
    print(key, u0_bit_len[key])

print("--- u1 bit")

for key in u1_bit_len.keys():
    print(key, u1_bit_len[key])
