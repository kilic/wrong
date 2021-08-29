import sympy
from random import randint


def new_reporter():
    reporter = {}
    reporter["fails"] = {}
    reporter["u0_bit_len"] = {}
    reporter["u1_bit_len"] = {}
    return reporter


class RNS:
    def setup(bit_len_modulus, T, number_of_limbs, bit_len_limb):

        while True:
            a = sympy.randprime(1 << (bit_len_modulus - 1),
                                1 << bit_len_modulus)
            b = sympy.randprime(1 << (bit_len_modulus - 1),
                                1 << bit_len_modulus)

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
            return RNS(
                wrong_modulus,
                native_modulus,
                number_of_limbs,
                bit_len_limb,
            )

    def __init__(
        self,
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

    def rand_int(self):
        return randint(0, self.wrong_modulus)

    def rand_limb(self):
        return randint(0, 1 << self.bit_len_limb)

    def to_limbs(self, n):
        return [
            n >> (self.bit_len_limb * i) & ((1 << self.bit_len_limb) - 1)
            for i in range(self.number_of_limbs)
        ]

    def from_limbs(self, limbs):
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i] * (2**(self.bit_len_limb * i))
        return acc

    def debug_limbs(self, desc, limbs):
        s = desc + " "
        for e in reversed(limbs):
            s += hex(e) + " "
        print(hex(self.from_limbs(limbs)), s)

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
        if (u0 & mask != 0) or (u1 & mask != 0):
            key = (self.wrong_modulus.bit_length(),
                   self.native_modulus.bit_length())
            fails = reporter["fails"]
            if key not in fails:
                fails[key] = 0
            fails[key] += 1

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
