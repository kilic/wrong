from rns import *
from setup import rand_rns

crt_modulus_bit_len = 32

u0_bit_len = {}
u1_bit_len = {}

for offset in range(1, crt_modulus_bit_len // 8 + 1):
    for _ in range(1000):

        rns = rand_rns(crt_modulus_bit_len, offset)
        p = rns.wrong_modulus
        bit_len_limb = rns.bit_len_limb
        R = rns.R
        t_ratio = rns.overflow_ratio()

        a = rns.rand()
        r, q, t, u0, u1 = a.reduce()
        assert a.value() == r.value()
        assert q == 0

        a = rns.max()
        r, q, t, u0, u1 = a.reduce()
        assert a.value() % p == r.value()
        assert q == t_ratio - 1

        a = rns.rand_in_max()
        r, q, t, u0, u1 = a.reduce()
        assert a.value() % p == r.value()
        assert q < t_ratio

        single_limb_reduction_bound = p.bit_length() - (crt_modulus_bit_len // 4) * 3 - 1

        a = rns.rand_with_limb_bit_size(bit_len_limb + single_limb_reduction_bound)
        r, q, t, u0, u1 = a.reduce()
        assert a.value() % p == r.value()
        assert q < R

        _u0 = u0.bit_length()
        _u1 = u1.bit_length()

        if _u0 not in u0_bit_len:
            u0_bit_len[_u0] = 0

        if _u1 not in u1_bit_len:
            u1_bit_len[_u1] = 0

        u0_bit_len[_u0] += 1
        u1_bit_len[_u1] += 1

    print("offset", offset)
    print("--- u0 bit")
    for key in u0_bit_len.keys():
        print(key, u0_bit_len[key])

    print("--- u1 bit")
    for key in u1_bit_len.keys():
        print(key, u1_bit_len[key])
    print("")
