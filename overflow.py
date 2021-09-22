def max_el(bit_len):
    return (1 << bit_len) - 1


bit_len = 8

print("mul")

k_a = 1
k_b = 1
p_bit_len = [bit_len, bit_len, bit_len, bit_len - 1]
p = [max_el(bit_len) for bit_len in p_bit_len]
q = (1 << bit_len) - 1

a = (1 << bit_len) - 1
b = (1 << bit_len) - 1
a = a * k_a
b = b * k_a

ab = a * b

t0 = ab + q * p[0]
t1 = 2 * ab + q * p[0] + q * p[1]
t2 = 3 * ab + q * p[0] + q * p[1] + q * p[2]
t3 = 4 * ab + q * p[0] + q * p[1] + q * p[2] + q * p[3]

u0 = t0 + (t1 << bit_len)
u1 = t2 + (t3 << bit_len)
u0 = u0 >> (2 * bit_len)
u1 = u1 >> (2 * bit_len)

print(u0.bit_length())
print(u1.bit_length())

print("red")

import sympy

bit_len_modulus = bit_len * 4 - 1
a = (1 << bit_len) - 1
k_a = 10

a = a * k_a
q = k_a
t = a + q * p[0]

u0 = t + (t << bit_len)
u1 = t + (t << bit_len)
u0 = u0 >> (2 * bit_len)
u1 = u1 >> (2 * bit_len)

print(u0.bit_length())
print(u1.bit_length())
