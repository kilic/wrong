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


from random import randint

bit_size = 8
# bound_bit_size = 32
R = 1 << bit_size
# R_bound = 1 << bound_bit_size
N = 4

p_val = 0xfedd
a_val = randint(0, p_val)
b_val = randint(0, p_val)
q_val = (a_val * b_val) // p_val
r_val = (a_val * b_val) % p_val
print("a", hex(a_val))
print("b", hex(b_val))
print("res", hex(r_val))
assert a_val * b_val == p_val * q_val + r_val

a = to_limbs(a_val, N, bit_size)
b = to_limbs(b_val, N, bit_size)
p = to_limbs(p_val, N, bit_size)
q = to_limbs(q_val, N, bit_size)
r = to_limbs(r_val, N, bit_size)

print("q", debug_limbs(q))
print("r", debug_limbs(r))

z1 = [0] * (2 * N - 1)
for i in range(N):
    for j in range(N):
        z1[i + j] += a[i] * b[j]
print("z1", debug_limbs(z1))

acc0 = 0
for i in range(len(z1)):
    acc0 += z1[i] * (1 << (bit_size * i))
assert acc0 % p_val == r_val

z2 = [0] * (2 * N - 1)
for i in range(N):
    for j in range(N):
        z2[i + j] += p[i] * q[j]
print("z2", debug_limbs(z2))

acc1 = 0
for i in range(len(z2)):
    acc1 += z2[i] * (1 << (bit_size * i))
assert acc1 + r_val == acc0

for i in range(len(r)):
    z2[i] += r[i]

assert from_limbs(z2, bit_size) == from_limbs(z1, bit_size)
print(debug_limbs(z2))
print(debug_limbs(z1))
print(from_limbs(z2, bit_size))
print(from_limbs(z1, bit_size))

u0 = (z1[0] - z2[0] + R * (z1[1] - z2[1]))
u1 = (z1[2] - z2[2] + R * (z1[3] - z2[3]))

print(hex(u0))
print(hex(u1))
