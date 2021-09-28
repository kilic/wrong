from rns import *
from setup import rand_rns


def red_test(iter, rns):

    u0_bit_len, u1_bit_len = {}, {}

    p = rns.wrong_modulus
    bit_len_limb = rns.bit_len_limb
    R = rns.R
    t_ratio = rns.overflow_ratio()

    for _ in range(iter):

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

        # single_limb_reduction_bound = p.bit_length() - bit_len_limb * 3 - 1
        bound = rns.single_limb_upper_bound()

        a = rns.rand_with_limb_bit_size(bound)
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

        assert bit_len_limb + 1 not in u0_bit_len
        assert bit_len_limb + 1 not in u1_bit_len

    print("--- u0 bit")
    for key in u0_bit_len.keys():
        print(key, u0_bit_len[key])

    print("--- u1 bit")
    for key in u1_bit_len.keys():
        print(key, u1_bit_len[key])


#
def test():
    crt_modulus_bit_len = 16

    for offset in range(1, crt_modulus_bit_len // 8 + 1):
        print("offset", offset)
        rns = rand_rns(crt_modulus_bit_len, offset)
        red_test(1000, rns)


# test()