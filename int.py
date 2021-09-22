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

        v0, v1, fails, overflow = self.residues(t, r)

        return Integer(self.rns, r), q, t, v0, v1, fails, overflow

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

        v0, v1, fails, overflow = self.residues(t, r)

        return Integer(self.rns, r), q, t, v0, v1, fails, overflow

    def residues(self, t, r):

        t_correct = t[:]
        b = self.rns.bit_len_limb
        T = self.rns.T

        for i, ri in enumerate(r):
            t_correct[i] = t[i] - ri

        acc = 0
        for i, ti in enumerate(t_correct):
            acc = acc + (ti << (b * i))
        assert acc % T == 0

        n = self.rns.native_modulus
        mask = self.rns.lsh(1, 2) - 1
        rns = self.rns

        intermediate_overflow = False
        u0 = (t[0] + rns.lsh(t[1]) - r[0] - rns.lsh(r[1]))
        u0_ = (t[0] + (t[1] << b)) - r[0] - (r[1] << b)

        u1 = (t[2] + rns.lsh(t[3]) - r[2] - rns.lsh(r[3]))
        u1_ = (t[2] + (t[3] << b)) - r[2] - (r[3] << b)

        if u0_ >= n or u1_ >= n:
            print(hex(n))
            print(hex(u0_))
            print(hex(u1_))
            intermediate_overflow = True

        u1 = (u1 + rns.rsh(u0, 2))

        fails = False
        if (u0 & mask != 0) or (u1 & mask != 0):
            fails = True

        v0 = rns.rsh(rns.rsh(u0))
        v1 = rns.rsh(rns.rsh(u1))

        return v0, v1, fails, intermediate_overflow

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
