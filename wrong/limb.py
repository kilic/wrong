from __future__ import annotations


class Limb:

    def zero(modulus) -> Limb:
        return Limb(0, modulus, 0)

    def new(value: int, modulus: int, max_val: int):
        assert max_val >= value
        assert modulus > value
        return Limb(value, modulus, max_val)

    def new_no_check(value: int, modulus: int, max_val: int):
        return Limb(value, modulus, max_val)

    def __init__(self, value: int, modulus: int, max_val: int):
        self.value = value
        self.modulus = modulus
        self.max_val = max_val

    def scale(self, k: int):
        self.value = self.value * k
        assert self.value < self.modulus
        self.max_val = self.max_val * k

    def __mul__(self, other: Limb) -> Limb:
        value = (self.value * other.value) % self.modulus
        max_val = self.max_val * other.max_val
        assert max_val < self.modulus
        return Limb.new(value, self.modulus, max_val)

    def __add__(self, other: Limb) -> Limb:
        value = (self.value + other.value) % self.modulus
        max_val = self.max_val + other.max_val
        # assert no wrap
        assert max_val < self.modulus
        return Limb.new(value, self.modulus, max_val)

    def __sub__(self, other: Limb) -> Limb:
        value = (self.value - other.value) % self.modulus
        max_val = self.max_val
        return Limb.new_no_check(value, self.modulus, max_val)
