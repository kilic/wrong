from random import randint
from rns import *

bit_len_limbs = 64
number_of_limbs = 4
crt_modulus_bit_len = bit_len_limbs * number_of_limbs
T = 1 << crt_modulus_bit_len
R = 1 << bit_len_limbs

wrong_modulus = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47
native_modulus = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001
rns = RNS.setup(wrong_modulus, native_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)
print("modulus bit len", wrong_modulus.bit_length())


def max():
    return (1 << crt_modulus_bit_len) - 1


def rand():
    return randint(0, T - 1)


def rand_valid():
    return randint(0, wrong_modulus)


a, b = max(), max()
print("max bit len", a.bit_length())
m = a * b
q = m // wrong_modulus
print("max quotient bit len", q.bit_length())

bn_rns = rns
