from wrong.limb import Limb
from wrong.rns import RNS, Range
from wrong.ecc import *
from test import *

number_of_limbs = 4
limb_size = 68

native_modulus = bn254_n
wrong_modulus = bn254_p


def test_various_bases():

    wrong_modulus = bn254_p    # self emulating
    RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    wrong_modulus = pasta_n
    RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    wrong_modulus = pasta_p
    RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    wrong_modulus = secp256k1_n
    RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    wrong_modulus = secp256k1_p
    RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)


def test_rns():
    rns(wrong_modulus, native_modulus)


def test_aux():
    aux(wrong_modulus, native_modulus)


def test_operations():
    operations(wrong_modulus, native_modulus)


def test_residues():
    residues(wrong_modulus, native_modulus)
