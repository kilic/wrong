import sympy
from random import randint
from int import Integer


def new_reporter():
    reporter = {}
    reporter["fails"] = {}
    reporter["u0_bit_len"] = {}
    reporter["u1_bit_len"] = {}
    return reporter


class RNS:

    def setup(
        bit_len_modulus,
        crt_modulus_bit_len,
        number_of_limbs,
        bit_len_limb,
    ):

        T = 1 << crt_modulus_bit_len

        while True:

            a = sympy.randprime(1 << (bit_len_modulus - 1), 1 << bit_len_modulus)
            b = sympy.randprime(1 << (bit_len_modulus - 1), 1 << bit_len_modulus)

            wrong_modulus, native_modulus = 0, 0
            if b < a:
                wrong_modulus = a
                native_modulus = b
            elif a < b:
                wrong_modulus = b
                native_modulus = a
            else:
                continue

            if T * native_modulus < wrong_modulus**2:
                continue

            try:
                rns = RNS(
                    crt_modulus_bit_len,
                    wrong_modulus,
                    native_modulus,
                    number_of_limbs,
                    bit_len_limb,
                )
                return rns
            except:
                continue

    def __init__(
        self,
        crt_modulus_bit_len,
        wrong_modulus,
        native_modulus,
        number_of_limbs,
        bit_len_limb,
    ):
        self.wrong_modulus = wrong_modulus
        self.native_modulus = native_modulus
        self.number_of_limbs = number_of_limbs
        self.bit_len_limb = bit_len_limb
        self.R = 1 << bit_len_limb
        self.T = 1 << crt_modulus_bit_len
        self.neg_wrong_modulus = (-wrong_modulus) % self.T
        assert self.T > self.wrong_modulus
        assert self.T > self.native_modulus

        range_correct_factor = self.R - 1
        aux = [_p * range_correct_factor for _p in self.to_limbs(wrong_modulus)]

        # there is a funny case where a limb of and aux is equal to zero
        # and therefore can't move limb of the result into the range :/
        # for now let's just disallow such setup
        for u in aux:
            if u == 0:
                raise "bad setup"

        self.aux = aux

    def integer_from_limbs(self, limbs):
        return Integer(self, limbs)

    def integer_from_value(self, value):
        limbs = self.to_limbs(value)
        assert self.from_limbs(limbs) == value
        return Integer(self, limbs)

    def rand_int(self, limit=-1):
        if limit == -1:
            limit = self.wrong_modulus
        value = randint(0, limit)
        return self.integer_from_value(value)

    def rand_limb(self):
        return randint(0, 1 << self.bit_len_limb)

    def to_limbs(self, n):
        mask = ((1 << self.bit_len_limb) - 1)
        return [n >> (self.bit_len_limb * i) & mask for i in range(self.number_of_limbs)]

    def from_limbs(self, limbs):
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i] * (1 << (self.bit_len_limb * i))
        return acc

    def neg_wrong_modulus_limbs(self):
        return self.to_limbs(self.neg_wrong_modulus)

    def overflow_factor(self):
        return self.T // self.wrong_modulus

    def debug_limbs(self, desc, limbs):
        s = ""
        for e in reversed(limbs):
            s += hex(e) + " "
        print(desc, hex(self.from_limbs(limbs)), s)

    def residues(self, t, r):
        assert self.number_of_limbs == 4
        assert len(t) >= 4
        assert len(r) == 4

        R = self.R
        S = self.bit_len_limb << 1
        n = self.native_modulus

        u0 = (t[0] + R * t[1] - r[0] - R * r[1]) % n
        u1 = (t[2] + R * t[3] - r[2] - R * r[3]) % n
        u1 = (u1 + (u0 >> S)) % n

        return u0, u1

    def check(self, t, r, reporter):
        # works only for this case
        assert self.number_of_limbs == 4

        R = self.R
        S = self.bit_len_limb << 1
        n = self.native_modulus

        u0 = (t[0] + R * t[1] - r[0] - R * r[1]) % n
        u1 = (t[2] + R * t[3] - r[2] - R * r[3]) % n
        u1 = (u1 + (u0 >> S)) % n

        mask = (1 << S) - 1

        failed = None
        if (u0 & mask != 0) or (u1 & mask != 0):
            key = (self.wrong_modulus.bit_length(), self.native_modulus.bit_length())
            fails = reporter["fails"]
            if key not in fails:
                fails[key] = 0
            fails[key] += 1

            failed = True

        u0 = u0 >> S
        u1 = u1 >> S

        _u0 = u0.bit_length()
        _u1 = u1.bit_length()

        u0_bit_len = reporter["u0_bit_len"]
        u1_bit_len = reporter["u1_bit_len"]

        if _u0 not in u0_bit_len:
            u0_bit_len[_u0] = 0

        if _u1 not in u1_bit_len:
            u1_bit_len[_u1] = 0

        u0_bit_len[_u0] += 1
        u1_bit_len[_u1] += 1

        return failed
