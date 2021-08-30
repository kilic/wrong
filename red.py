from wrong import *
from random import randint

u0_bit_len = {}
u1_bit_len = {}
fails = {}

crt_modulus_bit_len = 32

bit_len_modulus = 28
bit_len_limbs = 8
number_of_limbs = 4

reporter = new_reporter()

for z in range(1000):

    rns = RNS.setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
    n = rns.native_modulus
    p_val = rns.wrong_modulus

    a_val = p_val - 1

    assert rns.overflow_factor() > 0
    b = randint(1, rns.overflow_factor())
    c = randint(0, b - 1)

    a_val = a_val * b

    assert a_val < rns.T

    q = a_val // p_val
    q = q - c
    r_val = a_val % p_val
    r_val = r_val + c * p_val
    assert a_val == p_val * q + r_val

    a = rns.to_limbs(a_val)
    assert rns.from_limbs(a) == a_val
    p = rns.neg_wrong_modulus_limbs()
    r = rns.to_limbs(r_val)
    assert rns.from_limbs(r) == r_val

    t = [a[i] + q * p[i] for i in range(4)]

    rns.check(t, r, reporter)

print("--- u0 bit")

for key in reporter["u0_bit_len"].keys():
    print(key, reporter["u0_bit_len"][key])

print("--- u1 bit")

for key in reporter["u1_bit_len"].keys():
    print(key, reporter["u1_bit_len"][key])

print("--- fails?")

for key in reporter["fails"].keys():
    print(key, reporter["fails"][key])
