class Integer:

    def __init__(self, rns, limbs):
        self.rns = rns
        self.limbs = limbs

    def __mul__(self, other):

        self_val = self.value()
        other_val = other.value()
        p_val = self.wrong_modulus()
        q_val = (self_val * other_val) // p_val
        r_val = (self_val * other_val) % p_val
        assert self_val * other_val == p_val * q_val + r_val

        p = self.rns.neg_wrong_modulus_limbs()
        q = self.rns.to_limbs(q_val)
        r = self.rns.to_limbs(r_val)

        N = self.rns.number_of_limbs
        n = self.rns.native_modulus

        t = [0] * (2 * N - 1)
        for i in range(N):
            for j in range(N):
                k = self[i] * other[j]
                t[i + j] = (t[i + j] + self[i] * other[j] + p[i] * q[j]) % n

        u0, u1, fails = self.residues(t, r)

        return Integer(self.rns, r), q, t, u0, u1, fails

    def __add__(self, other):
        res = self.rns.integer_from_limbs([(a + b) % self.native_modulus() for (a, b) in zip(self.limbs, other.limbs)])
        assert res.value() == self.value() + other.value()
        return res

    def __sub__(self, other):
        n = self.rns.native_modulus
        aux = self.rns.aux
        r = [(a - b) % n for a, b in zip(self, other)]
        r = [(r + aux) % n for r, aux in zip(r, aux)]
        r = self.rns.integer_from_limbs(r)
        return r.reduce()

    def __getitem__(self, i):
        return self.limbs[i]

    def reduce(self, c=0):
        # assert self.value() < self.rns.T
        p = self.wrong_modulus()
        value = self.value()

        q = value // p
        q = q - c
        assert q < (1 << self.rns.bit_len_limb)
        r_val = value % p
        r_val = r_val + c * p
        assert value == p * q + r_val

        p = self.rns.neg_wrong_modulus_limbs()
        r = self.rns.to_limbs(r_val)
        assert self.rns.from_limbs(r) == r_val
        t = [a + q * p for (a, p) in zip(self.limbs, p)]

        u0, u1, fails = self.residues(t, r)

        return Integer(self.rns, r), q, t, u0, u1, fails

    def residues(self, t, r):
        S = 2 * self.rns.bit_len_limb
        u0, u1 = self.rns.residues(t, r)

        mask = (1 << S) - 1

        fails = False
        if (u0 & mask != 0) or (u1 & mask != 0):
            fails = True

        v0 = u0 >> S
        v1 = u1 >> S

        return v0, v1, fails

    def value(self):
        return self.rns.from_limbs(self.limbs)

    def wrong_modulus(self):
        return self.rns.wrong_modulus

    def native_modulus(self):
        return self.rns.native_modulus

    def debug(self, desc=""):
        s = ""
        for e in reversed(self.limbs):
            s += "\n" + hex(e)
        print(desc, s)
