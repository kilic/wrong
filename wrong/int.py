from __future__ import annotations


class Integer:

    def __init__(self, rns: RNS, limbs: list[Limb]):
        self.rns = rns
        self.limbs = limbs
        assert self.value() <= self.max_val()

    def __mul__(self, other: Integer) -> tuple[Integer, list[Limb], list[Limb], Limb, Limb]:

        self_val = self.value()
        other_val = other.value()
        p_val = self.wrong_modulus()

        q_val = (self_val * other_val) // p_val
        r_val = (self_val * other_val) % p_val
        assert self.rns.max_mul_quotient >= q_val

        N = self.rns.number_of_limbs
        p = self.rns.neg_wrong_modulus_limbs()
        q = self.rns.value_to_limbs(q_val, Range.MUL_QUOTIENT)
        r = self.rns.value_to_limbs(r_val)
        n = self.rns.native_modulus

        t = [Limb.zero(self.rns.native_modulus)] * (2 * N - 1)
        for i in range(N):
            for j in range(N):
                t[i + j] = t[i + j] + self[i] * other[j] + p[i] * q[j]

        v0, v1 = self.residues(t, r)

        must_be_zero = self.value() * other.value()
        must_be_zero = must_be_zero - p_val * q_val
        must_be_zero = must_be_zero - r_val
        assert must_be_zero % n == 0

        return self.rns.from_limbs(r), q, t, v0, v1

    def reduce(self) -> tuple[Integer, Limb, list[Limb], Limb, Limb]:
        p = self.wrong_modulus()
        value = self.value()

        q = (value // p)
        r = (value % p)

        p = self.rns.neg_wrong_modulus_limbs()
        r = self.rns.value_to_limbs(r)

        q = Limb(q, self.rns.native_modulus, self.rns.max_reduced_limb_val)

        t = [_a + q * _p for (_a, _p) in zip(self.limbs, p)]
        v0, v1 = self.residues(t, r)

        return self.rns.from_limbs(r), q, t, v0, v1

    def __add__(self, other: Integer) -> Integer:
        limbs = [a + b for (a, b) in zip(self, other)]
        res = Integer(self.rns, limbs)
        assert res.value() == self.value() + other.value()
        assert res.max_val() == self.max_val() + other.max_val()
        return res

    def __sub__(self, other: Integer) -> Integer:
        aux_limbs = self.rns.make_aux(other)
        limbs = [a - b for a, b in zip(self, other)]
        limbs = [r + aux for r, aux in zip(limbs, aux_limbs)]

        for limb in limbs:
            assert limb.value < self.rns.max_unreduced_limb_val

        return Integer(self.rns, limbs)

    def __getitem__(self, i: int) -> int:
        return self.limbs[i]

    def max_val(self):
        return self.rns.max_from_limbs(self.limbs)

    def apply_positive_aux(self) -> Integer:
        return self.rns.from_limbs([self.limbs[i] + self.rns.aux[i] for i in range(self.rns.number_of_limbs)])

    def apply_negative_aux(self) -> Integer:
        return self.rns.from_limbs([self.rns.aux[i] - self.limbs[i] for i in range(self.rns.number_of_limbs)])

    def must_reduce_by_sum(self) -> bool:
        return self.max_val() > self.rns.max_operand_value

    def must_reduce_by_a_limb(self) -> bool:

        ret = False
        for limb in self.limbs:
            ret = ret | (limb.max_val > self.rns.max_unreduced_limb_val)
        return ret

    def reduce_if_necessary(self) -> bool:
        if self.must_reduce():
            self.reduce()
            return True

        return False

    def residues(self, t: list[Limb], r: list[Limb]) -> tuple[Limb, Limb]:

        t_correct = t[:]
        b = self.rns.bit_len_limb
        T = self.rns.binary_modulus

        for i, ri in enumerate(r):
            t_correct[i] = t[i] - ri

        acc = 0
        for i, ti in enumerate(t_correct):
            acc = acc + (ti.value << (b * i))
        assert acc % T == 0

        n = self.rns.native_modulus
        mask = (1 << (b * 2)) - 1
        rns = self.rns

        u0 = (t[0] + rns.lsh(t[1]) - r[0] - rns.lsh(r[1]))
        u0_ = (t[0].value + (t[1].value << b)) - r[0].value - (r[1].value << b)

        u1 = (t[2] + rns.lsh(t[3]) - r[2] - rns.lsh(r[3]))
        u1_ = (t[2].value + (t[3].value << b)) - r[2].value - (r[3].value << b)

        assert u0_ < n
        assert u1_ < n

        u1 = (u1 + rns.rsh(u0, 2))

        assert u0.value & mask == 0
        assert u1.value & mask == 0

        v0 = rns.rsh(rns.rsh(u0))
        v1 = rns.rsh(rns.rsh(u1))

        return v0, v1

    def value(self) -> int:
        return self.rns.value_from_limbs(self.limbs)

    def native(self) -> int:
        return self.value() % self.rns.native_modulus

    def wrong_modulus(self) -> int:
        return self.rns.wrong_modulus

    def native_modulus(self) -> int:
        return self.rns.native_modulus

    def bits(self) -> int:
        return self.value().bit_length()

    def debug(self, desc: str = ""):
        s = desc + ": " + hex(self.value()) + "\n" + "["
        for e in self.limbs:
            s += hex(e) + ", "
        print(s, "]")


from wrong.limb import Limb
from wrong.rns import RNS, Range
