import sympy
from random import randint
from int import Integer
from py_ecc.utils import prime_field_inv


def new_reporter():
    reporter = {}
    reporter["fails"] = {}
    reporter["u0_bit_len"] = {}
    reporter["u1_bit_len"] = {}
    return reporter


class RNS:

    def setup2(
        wrong_modulus,
        native_modulus,
        crt_modulus_bit_len,
        number_of_limbs,
        bit_len_limb,
    ):
        T = 1 << crt_modulus_bit_len
        assert T * native_modulus > wrong_modulus**2
        return RNS(
            crt_modulus_bit_len,
            wrong_modulus,
            native_modulus,
            number_of_limbs,
            bit_len_limb,
        )

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

            return RNS(
                crt_modulus_bit_len,
                wrong_modulus,
                native_modulus,
                number_of_limbs,
                bit_len_limb,
            )

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
        self.left_shifter = 1 << bit_len_limb
        self.T = 1 << crt_modulus_bit_len
        self.neg_wrong_modulus = (-wrong_modulus) % self.T
        inv_two = prime_field_inv(2, native_modulus)
        self.right_shifter = (inv_two**(self.bit_len_limb)) % native_modulus

        assert self.T > self.wrong_modulus
        assert self.T > self.native_modulus

        range_correct_factor = self.left_shifter - 1
        modulus_limbs = self.to_limbs(wrong_modulus)
        aux = [_p * range_correct_factor for _p in modulus_limbs]

        # there is a funny case where a limb of and aux is equal to zero
        # and therefore can't move limb of the result into the range :/
        # so we borrow from next limb.
        self.fixed_aux = False

        for i in range(self.number_of_limbs):
            if aux[i] == 0:

                # First limb of modulus is zero. Non prime modulus apperently
                assert i != 0
                # Last limb of modulus is zero. We expect sparse setup
                assert i != self.number_of_limbs - 1

                this, next = i, i + 1
                b = self.bit_len_limb
                _aux = aux[:]
                aux[this] = ((1 << b) - 1) << b
                aux[next] = ((aux[next] << b) - aux[this]) >> b

                assert self.from_limbs(_aux) == self.from_limbs(aux)
                self.fixed_aux = True

        assert self.from_limbs(aux) % self.wrong_modulus == 0

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
        b = self.bit_len_limb
        mask = ((1 << b) - 1)
        return [n >> (b * i) & mask for i in range(self.number_of_limbs)]

    def from_limbs(self, limbs):
        b = self.bit_len_limb
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i] * (1 << (b * i))
        return acc

    def neg_wrong_modulus_limbs(self):
        return self.to_limbs(self.neg_wrong_modulus)

    def wrong_modulus_limbs(self):
        return self.to_limbs(self.wrong_modulus)

    def overflow_ratio(self):
        return self.T // self.wrong_modulus

    def debug_limbs(self, desc, limbs):
        s = ""
        for e in reversed(limbs):
            s += hex(e) + " "
        print(desc, hex(self.from_limbs(limbs)), s)

    def lsh(self, a, n=1):
        R = self.left_shifter**n
        return (a * R) % self.native_modulus

    def rsh(self, a, n=1):
        R = self.right_shifter**n
        return (a * R) % self.native_modulus
