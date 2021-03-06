from wrong.limb import Limb
from wrong.rns import RNS, Range
from wrong.ecc import *

number_of_limbs = 4
limb_size = 68


def aux(wrong_modulus: int, native_modulus: int):
    rns = RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    e = rns.max_remainder_int()
    aux_limbs = rns.make_aux(e)
    aux = rns.from_limbs(aux_limbs)
    assert aux.value() == rns.base_aux_val
    assert e.bits() + 1 == aux.bits()
    assert (e.value() + 1).bit_length() == aux.bits()

    for shift in range(20):
        limbs = e.limbs[:]
        a = rns.from_limbs(limbs)
        u = (1 << (a.limbs[number_of_limbs - 1].bits() + shift)) - 1
        a.limbs[number_of_limbs - 1] = rns.to_constant_limb(u)
        aux_limbs = rns.make_aux(a)
        aux = rns.from_limbs(aux_limbs)
        assert aux.bits() > a.bits()


def rns(wrong_modulus: int, native_modulus: int):
    rns = RNS.setup(limb_size, wrong_modulus, native_modulus, number_of_limbs)
    assert rns.max_remainder_value == rns.rand_in_remainder_range().max_val()
    assert rns.max_operand_value == rns.rand_in_operand_range().max_val()
    assert 0 == rns.base_aux_val % rns.wrong_modulus
    assert rns.rand_in_remainder_range().must_reduce_by_sum() is False
    assert rns.rand_in_operand_range().must_reduce_by_sum() is False

    w = rns.from_value(wrong_modulus, Range.CONSTANT)
    assert w.max_val() == wrong_modulus

    print(hex(rns.max_most_significant_reduced_limb_val))
    print(hex(rns.max_most_significant_operand_limb_val))
    print(hex(rns.max_most_significant_unreduced_limb_val))
    print(hex(rns.max_most_significant_mul_quotient_limb_val))

    print("max mul q")
    print(rns.max_mul_quotient.bit_length())
    print(hex(rns.max_mul_quotient))

    print("max mul operand")
    print(rns.max_operand_value.bit_length())
    print(hex(rns.max_operand_value))

    print("max remainder")
    print(rns.max_remainder_value.bit_length())
    print(hex(rns.max_remainder_value))


def reduction_limits(wrong_modulus: int, native_modulus: int):

    w = wrong_modulus
    n = native_modulus
    rns = RNS.setup(limb_size, w, n, number_of_limbs)
    print("xxx", hex(rns.max_unreduced_limb_val))
    print("xxx", rns.max_unreduced_limb_val.bit_length())

    limbs = [Limb.new(rns.max_unreduced_limb_val, rns.native_modulus, rns.max_unreduced_limb_val)] * rns.number_of_limbs
    a = rns.from_limbs(limbs)

    c, q, t, v0, v1 = a.reduce()
    q = q.value
    print(hex(q))
    print(q.bit_length())


def residues(wrong_modulus: int, native_modulus: int):

    #??mul

    w = wrong_modulus
    n = native_modulus
    rns = RNS.setup(limb_size, w, n, number_of_limbs)

    a = rns.max_operand_int()
    a = [l.max_val for l in a]
    for l in a:
        print(hex(l))

    p = [l.value for l in rns.neg_wrong_modulus_limbs()]
    q = [rns.max_reduced_limb_val, rns.max_reduced_limb_val, rns.max_reduced_limb_val, rns.max_most_significant_mul_quotient_limb_val]

    t = [0] * (2 * rns.number_of_limbs - 1)
    for i in range(rns.number_of_limbs):
        for j in range(rns.number_of_limbs):
            t[i + j] = t[i + j] + a[i] * a[j] + p[i] * q[j]

    b = rns.bit_len_limb
    u0 = t[0] + (t[1] << b)
    u1 = t[2] + (t[3] << b)

    u1 = u1 + (u0 >> (2 * b))

    v0 = u0 >> (2 * b)
    v1 = u1 >> (2 * b)

    print("mul v0", v0.bit_length())
    print("mul v1", v1.bit_length())

    # red

    a = [Limb.new(rns.max_unreduced_limb_val, rns.native_modulus, rns.max_unreduced_limb_val)] * rns.number_of_limbs
    value = rns.value_from_limbs(a)
    # print(hex(value))
    # print(hex(value // rns.wrong_modulus))
    q_max = (value // rns.wrong_modulus) + 1
    assert q_max < (1 << b)
    q = rns.max_reduced_limb_val

    a = [rns.max_unreduced_limb_val] * number_of_limbs
    t = [_a + q * _p for (_a, _p) in zip(a, p)]

    u0 = t[0] + (t[1] << b)
    u1 = t[2] + (t[3] << b)

    u1 = u1 + (u0 >> (2 * b))

    v0 = u0 >> (2 * b)
    v1 = u1 >> (2 * b)

    print("red v0", v0.bit_length())
    print("red v1", v1.bit_length())


def operations(wrong_modulus: int, native_modulus: int):
    w = wrong_modulus
    n = native_modulus

    rns = RNS.setup(limb_size, w, n, number_of_limbs)

    a = rns.rand_in_remainder_range()
    b = rns.rand_in_remainder_range()
    c = a + b
    assert c.value() == a.value() + b.value()
    assert c.max_val() == a.max_val() + b.max_val()
    assert c.native() == (a.native() + b.native()) % n
    assert c.must_reduce_by_sum() is False    # assume there is enough gap btw operand range and remainder range

    c = a - b
    aux = rns.make_aux(b)
    aux = rns.value_from_limbs(aux)
    assert c.value() % w == (a.value() - b.value()) % w
    assert c.max_val() == a.max_val() + aux
    assert c.native() == (aux + a.native() - b.native()) % n

    a = rns.rand_in_remainder_range()
    b = rns.rand_in_remainder_range()
    c, q, t, v0, v1 = a * b
    q = rns.value_from_limbs(q)
    assert a.value() * b.value() == q * w + c.value()

    a = rns.max_operand_int()
    b = rns.max_operand_int()
    c, q, t, v0, v1 = a * b
    q = rns.value_from_limbs(q)
    assert a.value() * b.value() == q * w + c.value()

    print("mul residues max bit len")
    print(v0.max_val.bit_length())
    print(v1.max_val.bit_length())

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
