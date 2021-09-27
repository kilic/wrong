from rns import *


def rand_rns(crt_modulus_bit_len, wrong_modulus_offset):
    bit_len_modulus = crt_modulus_bit_len - wrong_modulus_offset
    number_of_limbs = 4
    bit_len_limb = crt_modulus_bit_len // number_of_limbs
    return RNS.rand_setup(bit_len_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limb)
