from random import randint
import sympy
from sympy.sets.fancysets import Naturals


def to_limbs(n, number_of_limbs, R):
    return [n >> (R * i) & ((1 << R) - 1) for i in range(number_of_limbs)]


def from_limbs(limbs, R):
    acc = 0
    for i in range(len(limbs)):
        acc += limbs[i] * (2**(R * i))
    return acc


def debug_limbs(limbs):
    s = ""
    for e in reversed(limbs):
        s += hex(e) + " "
    return s


def setup(n, T):
    a = sympy.randprime(1 << (n - 1), 1 << n)
    b = sympy.randprime(1 << (n - 1), 1 << n)
    # dif = 2
    # b = sympy.randprime(1 << (n - dif - 1), 1 << (n - dif))
    if b < a:
        wrong_modulus = a
        native_modulus = b
        if T * native_modulus < wrong_modulus**2:
            return setup(n, T)
        return wrong_modulus, native_modulus
    if a < b:

        wrong_modulus = b
        native_modulus = a

        if T * native_modulus < wrong_modulus**2:
            return setup(n, T)
        return wrong_modulus, native_modulus

    return setup(n, T)


bit_size = 31
t = 32
N = 4
limb_bit_size = t // N
R = 1 << limb_bit_size
T = 1 << t

u0_bit_len = {}
u1_bit_len = {}
fails = {}

for z in range(10):

    wrong_modulus, native_modulus = setup(bit_size, T)
    # 4 (29, 25, '0x13dc5fcf', '0x1d28d91')
    # wrong_modulus = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
    # native_modulus = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001

    assert wrong_modulus > native_modulus
    assert T * native_modulus > wrong_modulus**2

    p_val = wrong_modulus
    a_val = randint(0, p_val)
    b_val = 17
    b_val = randint(0, p_val)
    q_val = (a_val * b_val) // p_val
    r_val = (a_val * b_val) % p_val
    assert a_val * b_val == p_val * q_val + r_val

    p_val = (-p_val) % T

    a = to_limbs(a_val, N, limb_bit_size)
    b = to_limbs(b_val, N, limb_bit_size)
    p = to_limbs(p_val, N, limb_bit_size)
    q = to_limbs(q_val, N, limb_bit_size)
    r = to_limbs(r_val, N, limb_bit_size)

    t = [0] * (2 * N - 1)
    for i in range(N):
        for j in range(N):
            t[i + j] = (t[i + j] + a[i] * b[j] + p[i] * q[j]) % native_modulus

    print(debug_limbs(t))

    u0 = (t[0] + R * t[1] - r[0] - R * r[1]) % native_modulus
    print(hex(u0))
    u1 = (t[2] + R * t[3] - r[2] - R * r[3]) % native_modulus
    u1 = (u1 + (u0 >> (2 * limb_bit_size))) % native_modulus
    print(hex(u1))

    s = (2 * limb_bit_size)
    mask = (1 << s) - 1
    if u0 & mask != 0:
        key = (wrong_modulus.bit_length(), native_modulus.bit_length())
        if key not in fails:
            fails[key] = 0
        fails[key] += 1

    if u1 & mask != 0:
        key = (wrong_modulus.bit_length(), native_modulus.bit_length())
        if key not in fails:
            fails[key] = 0
        fails[key] += 1

    # print(wrong_modulus.bit_length(), native_modulus.bit_length())
    u0 = u0 >> s
    u1 = u1 >> s

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

print("--- fails?")

for key in fails.keys():
    print(key, fails[key])

# z1 = [0] * (2 * N - 1)
# for i in range(N):
#     for j in range(N):
#         z1[i + j] = (a[i] * b[j] + z1[i + j]) % native_modulus

# print("z1", debug_limbs(z1))

# z2 = [0] * (2 * N - 1)
# for i in range(N):
#     for j in range(N):
#         z2[i + j] = (p[i] * q[j] + z2[i + j]) % native_modulus

# print("z2", debug_limbs(z2))

# for i in range(len(r)):
#     z2[i] = (z2[i] - r[i]) % native_modulus

# u0 = (z1[0] + z2[0] + R * (z1[1] + z2[1])) % native_modulus
# u1 = (z1[2] + z2[2] + R * (z1[3] + z2[3])) % native_modulus
# u1 = (u1 + (u0 >> (2 * limb_bit_size))) % native_modulus

# s = (2 * limb_bit_size)
# mask = 1 << (s - 1)
# assert u0 & mask == 0
# assert u1 & mask == 0
# u0 = u0 >> s
# u1 = u1 >> s
