from wrong.rns import RNS, Range
from wrong.ecc import *

number_of_limbs = 4
limb_size = 68
native_modulus = bn254_n


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
    wrong_modulus = bn254_p
    rns = RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    assert rns.max_remainder_value == rns.rand_in_remainder_range().max_val()
    assert rns.max_operand_value == rns.rand_in_operand_range().max_val()
    assert 0 == rns.aux_val % rns.wrong_modulus
    assert rns.rand_in_remainder_range().must_reduce_by_sum() is False
    assert rns.rand_in_operand_range().must_reduce_by_sum() is False

    w = rns.from_value(wrong_modulus, Range.CONSTANT)
    assert w.max_val() == wrong_modulus

    print("max mul q")
    print(rns.max_mul_quotient.bit_length())
    print(hex(rns.max_mul_quotient))

    print("max mul operand")
    print(rns.max_operand_value.bit_length())
    print(hex(rns.max_operand_value))

    print("max remainder")
    print(rns.max_remainder_value.bit_length())
    print(hex(rns.max_remainder_value))


def test_operations():
    w = bn254_p
    n = native_modulus
    rns = RNS.setup(limb_size, w, native_modulus, number_of_limbs)

    a = rns.rand_in_remainder_range()
    b = rns.rand_in_remainder_range()
    c = a + b
    assert c.value() == a.value() + b.value()
    assert c.max_val() == a.max_val() + b.max_val()
    assert c.native() == (a.native() + b.native()) % n
    assert c.must_reduce_by_sum() is False    # assume there is enough gap btw operand range and remainder range

    c = a - b
    assert c.value() % w == (a.value() - b.value()) % w
    assert c.max_val() == a.max_val() + rns.aux_val
    assert c.native() == (rns.aux_val + a.native() - b.native()) % n

    a = rns.rand_in_remainder_range()
    b = rns.rand_in_remainder_range()
    c, q, t, v0, v1 = a * b
    q = rns.value_from_limbs(q)
    assert a.value() * b.value() == q * w + c.value()

    print("mul residues max bit len")
    print(v0.max_val.bit_length())
    print(v1.max_val.bit_length())

    a = rns.max_operand_int()
    b = rns.max_operand_int()
    c, q, t, v0, v1 = a * b
    q = rns.value_from_limbs(q)
    assert a.value() * b.value() == q * w + c.value()

    a = rns.rand_in_remainder_range()
    for i in range(1000):
        a = a + a
        if (a.must_reduce_by_sum()):
            print("reduce by sum after double", i)
            c, q, t, v0, v1 = a.reduce()
            assert a.value() == q.value * w + c.value()
            print("quotient")
            print(hex(q.value))
            print(q.value.bit_length())
            print("red residues max bit len")
            print(v0.max_val.bit_length())
            print(v1.max_val.bit_length())
            break

    a = rns.rand_in_remainder_range()
    for i in range(1000):
        a = a + rns.rand_in_remainder_range()
        if (a.must_reduce_by_sum()):
            c, q, t, v0, v1 = a.reduce()
            print("reduce by sum after add", i)
            assert a.value() == q.value * w + c.value()
            print("quotient")
            print(hex(q.value))
            print(q.value.bit_length())
            print("red residues max bit len")
            print(v0.max_val.bit_length())
            print(v1.max_val.bit_length())
            break

    a = rns.rand_in_remainder_range()
    for i in range(1000):
        a = a + a
        if (a.must_reduce_by_a_limb()):
            c, q, t, v0, v1 = a.reduce()
            print("reduce by limb after double", i)
            assert a.value() == q.value * w + c.value()
            print("quotient")
            print(hex(q.value))
            print(q.value.bit_length())
            print("red residues max bit len")
            print(v0.max_val.bit_length())
            print(v1.max_val.bit_length())
            break

    # too much room for this op
    # a = rns.rand_in_remainder_range()
    # for i in range(1000):
    #     a = a + rns.rand_in_remainder_range()
    #     if (a.must_reduce_by_a_limb()):
    #         print("reduce by limb after add", i)
    #         assert a.value() == q.value * w + c.value()
    #         print("quotient")
    #         print(hex(q.value))
    #         print(q.value.bit_length())
    #         print("red residues max bit len")
    #         print(v0.max_val.bit_length())
    #         print(v1.max_val.bit_length())
    #         break

    a = rns.rand_in_remainder_range()
    for i in range(1000):
        a = a - rns.rand_in_remainder_range()
        if (a.must_reduce_by_sum()):
            c, q, t, v0, v1 = a.reduce()
            print("reduce by sum after sub", i)
            assert a.value() == q.value * w + c.value()
            print("quotient")
            print(hex(q.value))
            print(q.value.bit_length())
            print("red residues max bit len")
            print(v0.max_val.bit_length())
            print(v1.max_val.bit_length())
            break

    # too much room for this op too
    # a = rns.rand_in_remainder_range()
    # for i in range(1000):
    #     a = a - rns.rand_in_remainder_range()
    #     if (a.must_reduce_by_a_limb()):
    #         c, q, t, v0, v1 = a.reduce()
    #         print("reduce by limb after sub", i)
    #         assert a.value() == q.value * w + c.value()
    #         print("quotient")
    #         print(hex(q.value))
    #         print(q.value.bit_length())
    #         print("red residues max bit len")
    #         print(v0.max_val.bit_length())
    #         print(v1.max_val.bit_length())
    #         break
