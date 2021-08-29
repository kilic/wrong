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

    a_val = rns.rand_int()
    b_val = rns.rand_int()
    q_val = (a_val * b_val) // p_val
    r_val = (a_val * b_val) % p_val
    assert a_val * b_val == p_val * q_val + r_val

    neg_p_val = (-p_val) % T

    a = rns.to_limbs(a_val)
    b = rns.to_limbs(b_val)
    p = rns.to_limbs(neg_p_val)
    q = rns.to_limbs(q_val)
    r = rns.to_limbs(r_val)

    N = rns.number_of_limbs
    t = [0] * (2 * N - 1)
    for i in range(N):
        for j in range(N):
            t[i + j] = (t[i + j] + a[i] * b[j] + p[i] * q[j]) % n

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
