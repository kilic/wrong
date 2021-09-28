from random import randint
from rns import *

bit_len_limbs = 64
number_of_limbs = 4
crt_modulus_bit_len = bit_len_limbs * number_of_limbs

wrong_modulus = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
native_modulus = 0x40000000000000000000000000000000224698fc0994a8dd8c46eb2100000001
rns = RNS.setup(wrong_modulus, native_modulus, crt_modulus_bit_len, number_of_limbs, bit_len_limbs)

analyse(rns)
