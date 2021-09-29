import sympy
from random import randint
from int import Integer
from py_ecc.utils import prime_field_inv


class RNS:

    def setup(
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

    def rand_setup(
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
        self.R = self.left_shifter
        self.neg_wrong_modulus = (-wrong_modulus) % self.T
        inv_two = prime_field_inv(2, native_modulus)
        self.right_shifter = (inv_two**(self.bit_len_limb)) % native_modulus

        assert self.T > self.wrong_modulus
        assert self.T > self.native_modulus

        wrong_modulus_limbs = self.wrong_modulus_limbs()

        range_correct_factor = (self.R // wrong_modulus_limbs[self.number_of_limbs - 1]) + 1

        aux = [_p * range_correct_factor for _p in wrong_modulus_limbs]

        overborrow = False
        while True:
            for i in range(self.number_of_limbs):

                if aux[i] < self.R - 1:

                    if i == self.number_of_limbs - 1:
                        overborrow = True
                        print("overborrow")
                        break

                    aux[i] = aux[i] + self.R
                    aux[i + 1] -= 1

            if overborrow:
                range_correct_factor += 1
                aux = [_p * range_correct_factor for _p in wrong_modulus_limbs]
                overborrow = False
            else:
                break

        for _aux in aux:
            assert _aux >= self.R - 1

        assert self.value_from_limbs(aux) % self.wrong_modulus == 0

        self.aux = aux

    def from_limbs(self, limbs):
        return Integer(self, limbs)

    def from_value(self, value):
        limbs = self.value_to_limbs(value)
        assert self.value_from_limbs(limbs) == value
        return Integer(self, limbs)

    def rand(self):
        value = randint(0, self.wrong_modulus - 1)
        return self.from_value(value)

    def rand_in_max(self):
        value = randint(0, self.T - 1)
        return self.from_value(value)

    def rand_with_limb_bit_size(self, bit_len=0):
        return self.from_limbs([self.rand_limb(bit_len) for _ in range(self.number_of_limbs)])

    def max(self, bit_len=0):
        if bit_len == 0:
            bit_len = self.bit_len_limb
        return self.from_limbs([self.max_limb(bit_len)] * self.number_of_limbs)

    def max_limb(self, bit_len=0):
        if bit_len == 0:
            bit_len = self.bit_len_limb
        return (1 << bit_len) - 1

    def zero(self):
        return self.from_limbs([0] * self.number_of_limbs)

    def rand_limb(self, bit_len=0):
        bit_len = bit_len if bit_len != 0 else self.bit_len_limb
        return randint(0, (1 << bit_len) - 1)

    def value_to_limbs(self, n, number_of_limbs=0):
        if number_of_limbs == 0:
            number_of_limbs = self.number_of_limbs
        b = self.bit_len_limb
        mask = ((1 << b) - 1)
        return [n >> (b * i) & mask for i in range(number_of_limbs)]

    def value_from_limbs(self, limbs):
        b = self.bit_len_limb
        acc = 0
        for i in range(len(limbs)):
            acc += limbs[i] * (1 << (b * i))
        return acc

    def neg_wrong_modulus_limbs(self):
        return self.value_to_limbs(self.neg_wrong_modulus)

    def wrong_modulus_limbs(self):
        return self.value_to_limbs(self.wrong_modulus)

    def overflow_ratio(self):
        return (self.T // self.wrong_modulus) + 1

    def debug_limbs(self, desc, limbs):
        s = ""
        for e in reversed(limbs):
            s += hex(e) + " "
        print(desc, hex(self.value_from_limbs(limbs)), s)

    def lsh(self, a, n=1):
        R = self.left_shifter**n
        return (a * R) % self.native_modulus

    def rsh(self, a, n=1):
        R = self.right_shifter**n
        return (a * R) % self.native_modulus

    def single_limb_upper_bound(self):
        # TODO: reserch more on this val
        return self.wrong_modulus.bit_length() - self.bit_len_limb * 2 - 2
        # return self.bit_len_limb + self.bit_len_limb // 8


def analyse(rns):
    from red import red_test
    from mul import mul_test

    print("modulus bit len", rns.wrong_modulus.bit_length())

    for a in rns.aux:
        print("aux:", hex(a))

    T = rns.T
    R = rns.R

    a = rns.max()
    a.debug("a max in T")

    a = a.value()
    b = rns.max().value()
    p = rns.wrong_modulus
    c = a * b
    q = c // rns.wrong_modulus
    assert q > T

    bound = rns.single_limb_upper_bound()
    print("upper bound", bound)
    a = rns.max(bound)
    a.debug("a max in overflow")
    a = a.value()
    q_val = a // rns.wrong_modulus
    print(hex(q_val), q_val == R)
    assert q_val < R

    # bound += 1
    # a = rns.max(bound).value()
    # q_val = a // rns.wrong_modulus
    # assert q_val > R

    a = rns.max(bound)
    a_val = a.value()
    q = a_val // rns.wrong_modulus

    print("intermediates for max number:")
    r = 0
    p = rns.wrong_modulus_limbs()
    t_0 = a[0] + p[0] * q
    t_1 = a[1] + p[1] * q
    u_0 = (t_0 - r) + R * (t_1 - r)
    print("u 0 bit len", u_0.bit_length())
    v_0 = u_0 // (R * R)
    print("v 0 bit len", v_0.bit_length())

    t_2 = a[2] + p[2] * q
    t_3 = a[3] + p[3] * q
    u_1 = (t_2 - r) + R * (t_3 - r)
    print("u_1 bit len", u_1.bit_length())
    v_1 = (u_1 // (R**2)) + (u_0 // (R**4))
    print("v_1 bit len", v_1.bit_length())

    print("red test")
    red_test(100000, rns)
    print("mul test")
    mul_test(100000, rns)
