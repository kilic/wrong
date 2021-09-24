from rns import *

crt_modulus_bit_len = 32
bit_len_modulus = 31
bit_len_limbs = 8
number_of_limbs = 4

u0_bit_len = {}
u1_bit_len = {}
c_adjusted = {}

for z in range(1000):

    rns = RNS.setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
    p = rns.wrong_modulus
    T = rns.T

    a = rns.rand_int()
    b = rns.rand_int()
    c = a + b
    assert c.value() % p == (a.value() + b.value()) % p

    z = rns.integer_from_value(p - 1)
    acc = rns.integer_from_value(0)
    for i in range(256):
        acc = acc + z

    r0 = acc.value() % p

    r1, q, _, u0, u1, c, fails, overflow = acc.reduce()
    if fails:
        print("fail")
        print(overflow)
        print(u0.bit_length())
        print(u1.bit_length())
        break

    assert r0 == r1.value()

    _u0 = u0.bit_length()
    _u1 = u1.bit_length()

    if _u0 not in u0_bit_len:
        u0_bit_len[_u0] = 0

    if _u1 not in u1_bit_len:
        u1_bit_len[_u1] = 0

    if c not in c_adjusted:
        c_adjusted[c] = 0

    c_adjusted[c] += 1
    u0_bit_len[_u0] += 1
    u1_bit_len[_u1] += 1

print("--- u0 bit")

for key in u0_bit_len.keys():
    print(key, u0_bit_len[key])

print("--- u1 bit")

for key in u1_bit_len.keys():
    print(key, u1_bit_len[key])

print("--- c")

for key in c_adjusted.keys():
    print(key, c_adjusted[key])