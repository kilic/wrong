from __future__ import annotations
from random import randint
from py_ecc.utils import prime_field_inv
from enum import Enum


class Range(Enum):
    REMAINDER = 1
    OPERAND = 2
    MUL_QUOTIENT = 3
    CONSTANT = 4


class RNS:

    def setup(
        bit_len_limb: int,
        wrong_modulus: int,
        native_modulus: int,
        number_of_limbs: int,
    ) -> RNS:
        return RNS(
            bit_len_limb,
            wrong_modulus,
            native_modulus,
            number_of_limbs,
        )

    def calculate_aux(self) -> list[Limb]:

        R = self.left_shifter
        wrong_modulus_limbs = self.wrong_modulus_limbs()
        number_of_limbs = self.number_of_limbs

        range_correct_factor = (R // wrong_modulus_limbs[number_of_limbs - 1].value) + 1

        aux = [_p.value * range_correct_factor for _p in wrong_modulus_limbs]

        overborrow = False
        while True:
            for i in range(number_of_limbs):

                if aux[i] < R - 1:

                    if i == number_of_limbs - 1:
                        overborrow = True
                        print("overborrow")
                        break

                    aux[i] = aux[i] + R
                    aux[i + 1] -= 1

            if overborrow:
                range_correct_factor += 1
                aux = [_p * range_correct_factor for _p in wrong_modulus_limbs]
                overborrow = False
            else:
                break

        for _aux in aux:
            assert _aux >= R - 1

        return [Limb(e, self.wrong_modulus, e) for e in aux]

    def __init__(
        self,
        bit_len_limb: int,
        wrong_modulus: int,
        native_modulus: int,
        number_of_limbs: int,
    ):

        self.bit_len_limb = bit_len_limb
        self.binary_modulus_bit_len = bit_len_limb * number_of_limbs
        self.wrong_modulus = wrong_modulus
        self.native_modulus = native_modulus
        self.number_of_limbs = number_of_limbs
        self.bit_len_limb = bit_len_limb
        self.left_shifter = 1 << bit_len_limb
        self.binary_modulus = 1 << self.binary_modulus_bit_len
        self.R = self.left_shifter
        self.neg_wrong_modulus = (-wrong_modulus) % self.binary_modulus
        inv_two = prime_field_inv(2, native_modulus)
        self.right_shifter = (inv_two**(self.bit_len_limb)) % native_modulus

        assert self.binary_modulus > self.wrong_modulus
        assert self.binary_modulus > self.native_modulus
        assert self.binary_modulus * native_modulus > wrong_modulus**2

        # max_remainder_value < (1 << w_bits)
        # `n * T > q * w + max_remainder_value` to derive `max_quotient`
        # `max_quotient * w + max_remainder_value > a * b` to derive `max_mul_operand`

        self.nT = self.binary_modulus * self.native_modulus
        nT_bit_len = self.nT.bit_length()
        wrong_modulus_bit_len = wrong_modulus.bit_length()

        # n * T > a' * a'
        max_operand_bit_len_pre_q = (nT_bit_len // 2) - 1
        max_operand_value_pre_q = (1 << max_operand_bit_len_pre_q) - 1

        assert self.nT > (max_operand_value_pre_q * max_operand_value_pre_q)
        assert max_operand_value_pre_q > wrong_modulus

        # n * T > q*w + r
        self.max_remainder_value = (1 << wrong_modulus_bit_len) - 1
        max_mul_quotient_raw = (self.nT - self.max_remainder_value) // wrong_modulus
        self.max_mul_quotient = (1 << (max_mul_quotient_raw.bit_length() - 1)) - 1
        assert self.nT > (self.max_mul_quotient * wrong_modulus) + self.max_remainder_value
        assert self.max_mul_quotient > wrong_modulus

        # max_mul_quotient * w + r > a*b
        self.max_operand_bit_len = ((self.max_mul_quotient * wrong_modulus + self.max_remainder_value).bit_length() // 2) - 1
        self.max_operand_value = (1 << self.max_operand_bit_len) - 1

        assert self.max_operand_value <= max_operand_value_pre_q
        assert self.max_operand_value > wrong_modulus
        assert self.nT > (self.max_operand_value * self.max_operand_value)
        assert (self.max_mul_quotient * wrong_modulus) > (self.max_operand_value * self.max_operand_value)
        assert (self.max_mul_quotient * wrong_modulus + self.max_remainder_value) > (self.max_operand_value * self.max_operand_value)

        self.max_reduced_limb_val = (1 << bit_len_limb) - 1
        # TODO: this is just a placeholder not so accurate
        self.max_unreduced_limb_val = (1 << (bit_len_limb + bit_len_limb // 2)) - 1

        self.max_most_significant_reduced_limb_val = self.max_remainder_value >> (3 * bit_len_limb)
        self.max_most_significant_operand_limb_val = self.max_operand_value >> (3 * bit_len_limb)
        # TODO: this is just a placeholder not so accurate
        self.max_most_significant_unreduced_limb_val = self.max_unreduced_limb_val
        self.max_most_significant_mul_quotient_limb_val = self.max_mul_quotient >> (3 * bit_len_limb)

        acc = 0
        for i in range(number_of_limbs - 1):
            acc += self.max_reduced_limb_val << (self.bit_len_limb * i)
        acc += self.max_most_significant_reduced_limb_val << (self.bit_len_limb * (number_of_limbs - 1))
        assert acc == self.max_remainder_value

        acc = 0
        for i in range(number_of_limbs - 1):
            acc += self.max_reduced_limb_val << (self.bit_len_limb * i)
        acc += self.max_most_significant_mul_quotient_limb_val << (self.bit_len_limb * (number_of_limbs - 1))
        assert acc == self.max_mul_quotient

        self.aux_limbs = self.calculate_aux()
        self.aux_val = self.value_from_limbs(self.aux_limbs)
        assert self.aux_val % self.wrong_modulus == 0

    def max_limb(self, bit_len=0):
        if bit_len == 0:
            bit_len = self.bit_len_limb
        return (1 << bit_len) - 1

    def rand_limb(self, bit_len=0):
        bit_len = bit_len if bit_len != 0 else self.bit_len_limb
        return randint(0, (1 << bit_len) - 1)

    def max_most_significant_limb_val(self, overflow=Range.REMAINDER) -> int:
        if overflow == Range.REMAINDER:
            return self.max_most_significant_reduced_limb_val
        elif overflow == Range.OPERAND:
            return self.max_most_significant_operand_limb_val
        elif overflow == Range.MUL_QUOTIENT:
            return self.max_most_significant_mul_quotient_limb_val

        assert False

    def from_limbs(self, limbs: list[Limb]) -> Integer:
        return Integer(self, limbs)

    def from_value(self, value: int, overflow=Range.REMAINDER) -> Integer:
        limbs = self.value_to_limbs(value, overflow)
        assert self.value_from_limbs(limbs) == value
        return self.from_limbs(limbs)

    def max_remainder_int(self):
        return self.from_value(self.max_remainder_value, Range.REMAINDER)

    def max_operand_int(self):
        return self.from_value(self.max_operand_value, Range.OPERAND)

    def rand_in_field(self) -> Integer:
        value = randint(0, self.wrong_modulus - 1)
        return self.from_value(value)

    def rand_in_remainder_range(self) -> Integer:
        value = randint(0, self.max_remainder_value)
        return self.from_value(value, Range.REMAINDER)

    def rand_in_operand_range(self) -> Integer:
        value = randint(0, self.max_operand_value)
        return self.from_value(value, Range.OPERAND)

    def rand_with_limb_bit_size(self, bit_len: int = 0, overflow=Range.REMAINDER) -> Integer:
        return self.from_limbs([self.rand_limb(bit_len) for _ in range(self.number_of_limbs)], overflow)

    def zero(self) -> Integer:
        return self.from_limbs([0] * self.number_of_limbs)

    def value_to_limbs(self, n: int, overflow=Range.REMAINDER) -> list[Limb]:
        is_constant = overflow == Range.CONSTANT
        b = self.bit_len_limb
        mask = ((1 << b) - 1)
        limbs = []
        for i in range(self.number_of_limbs):
            value = n >> (b * i) & mask
            if i == self.number_of_limbs - 1:
                limbs.append(Limb(value, self.native_modulus, value if is_constant else self.max_most_significant_limb_val(overflow)))
            else:
                limbs.append(Limb(value, self.native_modulus, value if is_constant else self.max_limb()))

        return limbs

    def value_from_limbs(self, limbs: list[Limb]) -> int:
        b = self.bit_len_limb
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i].value * (1 << (b * i))
        return acc

    def max_from_limbs(self, limbs: list[Limb]) -> int:
        b = self.bit_len_limb
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i].max_val * (1 << (b * i))
        return acc

    def neg_wrong_modulus_limbs(self) -> list[Limb]:
        b = self.bit_len_limb
        mask = ((1 << b) - 1)
        limbs = []
        for i in range(self.number_of_limbs):
            value = self.neg_wrong_modulus >> (b * i) & mask
            limbs.append(Limb(value, self.native_modulus, value))
        return limbs

    def wrong_modulus_limbs(self) -> list[Limb]:
        b = self.bit_len_limb
        mask = ((1 << b) - 1)
        limbs = []
        for i in range(self.number_of_limbs):
            value = self.wrong_modulus >> (b * i) & mask
            limbs.append(Limb(value, self.native_modulus, value))
        return limbs

    def overflow_ratio(self) -> int:
        return (self.binary_modulus // self.wrong_modulus) + 1

    def debug_limbs(self, desc: str, limbs: list[Limb]):
        s = ""
        for e in reversed(limbs):
            s += hex(e) + " "
        print(desc, hex(self.value_from_limbs(limbs)), s)

    def lsh(self, a: Limb, n: int = 1):
        R = self.left_shifter**n
        value = (a.value * R) % self.native_modulus
        max_val = a.max_val << (self.bit_len_limb * n)
        return Limb(value, self.native_modulus, max_val)

    def rsh(self, a: Limb, n: int = 1):
        R = self.right_shifter**n
        value = (a.value * R) % self.native_modulus
        max_val = a.max_val >> (self.bit_len_limb * n)
        return Limb(value, self.native_modulus, max_val)


from wrong.int import Integer
from wrong.limb import Limb
