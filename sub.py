from wrong import *

u0_bit_len = {}
u1_bit_len = {}
fails = {}

crt_modulus_bit_len = 32
T = 1 << crt_modulus_bit_len

bit_len_modulus = 31
bit_len_limbs = 8
number_of_limbs = 4

reporter = new_reporter()

for z in range(1000):

    rns = RNS.setup(bit_len_modulus, T, number_of_limbs, bit_len_limbs)
    n = rns.native_modulus
    p_val = rns.wrong_modulus

    range_correct_factor = rns.R
    aux = [_p * range_correct_factor for _p in rns.to_limbs(p_val)]

    # there is a funny case where and aux can't move a limb into the range :/
    bad_aux = False
    for u in aux:
        if u == 0:
            bad_aux = True
    if bad_aux:
        continue

    neg_p_val = (-p_val) % T
    p = rns.to_limbs(neg_p_val)

    a_val = rns.rand_int()
    b_val = rns.rand_int()

    r_expect = (a_val - b_val) % p_val

    a = rns.to_limbs(a_val)
    b = rns.to_limbs(b_val)
    a = [(a - b) % rns.native_modulus for a, b in zip(a, b)]
    a = [(a + aux) % rns.native_modulus for a, aux in zip(a, aux)]

    a_val = rns.from_limbs(a)
    q = a_val // p_val
    r_val = a_val % p_val
    r = rns.to_limbs(r_val)
    assert a_val == p_val * q + r_val

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
