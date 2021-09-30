# Wrong Field

This uncomplete and draft wrong field implementation spec is mostly targetting ~256 bit base field on ~256 bit operation field such as BN254, secpk256 base fields on BN254 scalar field. And [solution from AZTEC](https://hackmd.io/@arielg/B13JoihA8) team is closely followed.

In layouts we use simple standart 4 width plonk gate with single further cell customization in `column_d`.

```
a * q_a + b * q_b + a * b * q_mul + c * q_c + d * q_d + d_next * q_d_next + q_constant = 0
```

## Definitions

`number_of_limbs`: For now we are only considering 4 limbs.

`b`: In sake of simplycity and convention limbs will be 64 bit.

`B = 1 << b`

`n`: Native field modulus.

`p`: Wrong field modulus.

`t = 256`

`T = 2^256`

`number_of_limbs_lookup`: to follow simplified approach above number of limbs for limb decomposion will be 4.

`b_lookup`: Again to follow simplified approach above number of lookup limbs will be `b/number_of_limbs_lookup = 16`.

`L = 1 << b_lookup`

> RESEARCH: Where does 68 bit limb and 110 bit overflow size come from that is used in barretenberg and franklin-crypto?

### Integer

An integer `a` is represented as 4 limbs `a = [a_3, a_2, a_1, a_0]` where it's actually a decomposion `a = a_3 * B^3 + a_2 * B^2 a_1 * B + a_0`.

Limb sizes of and integer can go beyond `[0, B)` as a result of addition and subtraction operations. We address the bounds of maximum limb size in Prenormalization section.

`p'` is the negative wrong modulus value and our only constant integer value:

`p' = T - p = [p'_3, p'_2, p'_1, p'_0]`

We mostly expect an integer `a < T` as an operand and call it prenormalized integer while normalized integer satisfies `a < p`.

## Range

We will need to constaint some cells to be in `[0,B)` or `[0,B + overflow]`. Notice that `B = 4 * (1 << b_lookup)` and then we decompose `b` bit value into 4 `b_lookup` values. Overflow part of the range is smaller than a lookup chunk so let's  `b_overflow < b_lookup`.

`u = (u_3 * L^3 + u_2 * L^2 * u_1 * L + u_0) + L^4 * overflow`.

To constain an integer to be in prenormalized form `a < T` rather than the to be an actual field element `a < p`. So each limb of and integer is decomposed in smaller 4 chunks. And these chunks are checked if they are in lookup table and then we recompose the limb with values int the table and check if it is equal to proposed limb.

### Layout

Notice that we will use further cells in `column_d` to check recomposition.

| A  | B  | C        | D  |
| -- | -- | -------- | -- |
| u1 | u2 | u3       | u4 |
| -  | -  | overflow | u  |

Cost: 2 rows for a limb, 8 rows for an intger

## Addition

Addition is straight forward:

`c = a + b = [a_i + b_i]`

Modular reduction is not neccerarily applied right after the addition. It leaves us some room for lazy operations. So maximum bit lenght of the result is increased by 1.

### Layout of addition

| A  | B  | C  | D |
| -- | -- | -- | - |
| a1 | b1 | c1 | - |
| a2 | b2 | c2 | - |
| a3 | b3 | c3 | - |
| a4 | b4 | c4 | - |

Cost: 4 rows

## Prenormalize

`a = q * p + r` equation illustrates the prenormalization approach. `a` is the input value and `p` is a hardwired constant while the quotient `q` and the result `r` are witnesses.

Since strict reduction down to `[0, p)` range is not applied we prefer call this operation as prenormalization. In general case

```
a = (q - β) * p + (r + β * p)
q' = (q - β)
r' = (r + β * p)
```

Whatever the shift value `β` is set, result `r` is always in `[0, T)`.

__Constrain__: `r_i` to be in `[0, B)`.

We must also consider size of the quotient `q` which is a dependent of maximumum number of add chain or in other words maximum bit size of limbs allowed. So just before a max value of an integer can go beyond a value that cannot be constructed with `q`, `p` and `r` where `q` is out of allowed bounds and `r` is in `[0, T)` it should be prenormalized.

Let's give an example where `q` is `b` bit value and `a` is overflown input can be decomposed as:

`a = a_3H * B^4 + (a_3L + a_2H) * B^3 + (a_2L + a_1H) * B^2 + (a_1L + a_0H) * B + a_0L`

Where we actually first decompose `a_i` as `a_i = B * a_iH + a_iL`. First term `a_3H * B^4` dominates the max bit size and it is `max_bit_size = bit_size(a_3H) + 4 * b + 1`. And bit size of the other side of the equation `q*p` is `bit_size(q) + bit_size_modulus`, So:

`bit_size(a_3H) = bit_size(q) + bit_size_modulus - 4*b - 1`.

And then we calculate maximum allowed bit size of a limb adding lower part of the limb: `bit_size(a_3H) + b`

__Constrain__: `q` to be in `[0, Q)`. Where `Q = 1 << max_allowed_q_size`.

Following similar rules with multiplication below intermediate values are:

```
t_0 = a_0 + p'_0 * q
t_1 = a_1 + p'_1 * q
t_2 = a_2 + p'_2 * q
t_3 = a_3 + p'_3 * q
u_0 = t_0 + t_1 * B - r_0 - r_1 * B
u_1 = t_2 + t_3 * B - r_2 - r_3 * B
```

__Constrain__: first `2b` bits of `u_0` is zero

__Constrain__: first `2b` bits of `u_1 + u_0 / R^2` is zero

```
v_0 * 2R = u_0
v_1 * 2R = u_1 + v_0
```

__Constrain__:`v_0` is in `[0, B + overflow_0)`

__Constrain__:`v_1` is in `[0, B + overflow_1)`

> TODO: about `overflow_i` values in __prenormalization__

### Layout of prenormalization

| A   | B   | C   | D   |
| --- | --- | --- | --- |
| a_0 | q   | t_0 | -   |
| a_1 | q   | t_1 | -   |
| a_2 | q   | t_2 | -   |
| a_3 | q   | t_3 | -   |
| t_0 | t_1 | r_0 | r_1 |
| -   | -   | v_0 | u_0 |
| t_2 | t_3 | r_2 | r_3 |
| -   | v_1 | v_0 | u_1 |

> TODO: selectors

Note that range checks are not in the layout.

Cost: 8 + 3 * limb_range_check + 1 * integer_range_check = 24 rows

## Subtraction

Limbs of all operands are expected to be in `[0, B)`

We apply subtraction as `c = a - b + aux` with a range correction aux value where moves result limbs to the correct range. We must pick an `aux` value which is a multiple of the modulus. Moreover a limb of `aux_i` must bring back underflown limb of a result back to the range where we can prenormalize the result integer back to `[0, T)`. So simply `aux_i` must be larger than `B`.

`c = a - b = [a_i - b_i + aux_i]`

So, corrected result `c_i` will be in `[0,2B)`. To continiue working with same integer we might apply prenormalization to the intermediate result `c` in order to reduce the result back to `[0,T)`.

### Layout of subtraction

| A  | B  | C  | D |
| -- | -- | -- | - |
| a1 | b1 | c1 | - |
| a2 | b2 | c2 | - |
| a3 | b3 | c3 | - |
| a4 | b4 | c4 | - |

Notice that `p * aux` is constant and values are placed in fixed columns.

Cost: 4 rows

## Multiplication

Multiplication will be constrained as `a * b = q * p + r` where `q` and `r` witness values. Notice that prover also can use shifted quotient and result values as it also happens in subtraction. Operands of multiplication must be in `[0, T)`.

```
a = (q - β) * p + (r + β * p)
q' = (q - β)
r' = (r + β * p)
```

* constaint `q'_i` in `[0, B)`
* constaint `r'_i` in `[0, B)`

With that range constaints we are sure that our result is in `[0, T)`. Which is sufficient to work with result integer in all operations. Also notice that `q'` can be larger that `T` since two integer in `[0, T)` multiplied. Then `q'` is represented with `number_of_limbs + 1` limbs. However the last limb of the `q'` has nothing to do with result limbs and intermediate values calculated below.


Here we rewrite intermediate value equations as in [AZTEC solution](https://hackmd.io/@arielg/B13JoihA8).

```
t_0 = a_0 * b_0 + p'_0 * q_0
t_1 = a_0 * b_1 + a_1 * b_0 + p'_0 * q_1 + p'_1 * q_0
t_2 = a_0 * b_2 + a_1 * b_1 + a_2 * b_0 + p'_0 * q_2 + p'_1 * q_1 + p'_2 * q_0
t_3 = a_0 * b_3 + a_1 * b_2 + a_2 * b_1 + a_3 * b_0 + p'_0 * q_3 + p'_1 * q_2 + p'_2 * q_1 + p'_3 * q_0
```

After having intermediate values the rest goes same as we did in prenormalization except different overflow range constaints.

> TODO: about `overflow_i` values in __multiplication__

### Layout of multiplication

| A   | B   | C   | D     |
| --- | --- | --- | ----- |
| a_0 | b_0 | q_0 | t_0   |
| a_0 | b_1 | q_1 | t_1   |
| a_1 | b_0 | q_0 | tmp   |
| a_0 | b_2 | q_2 | t_2   |
| a_1 | b_1 | q_1 | tmp_a |
| a_2 | b_0 | q_0 | tmp_b |
| a_0 | b_3 | q_3 | t_3   |
| a_1 | b_1 | q_2 | tmp_b |
| a_2 | b_2 | q_1 | tmp_a |
| a_3 | b_0 | q_0 | tmp_c |
| t_0 | t_1 | r_0 | r_1   |
| -   | -   | v_0 | u_0   |
| t_2 | t_3 | r_2 | r_3   |
| -   | v_1 | v_0 | u_1   |

> TODO: selectors

Cost: 14 + 2 * limb_range_check + 2 * integer_range_check = 34 rows


## Example

Public Inputs: `a`, `b`, `c` are in `[0,p)`

Circuit:

`c == a^3 + 2*a - b^2`

```
1. t0 = a * a    // t0 in [0,T)
2. t1 = t0 * a   // t1 in [0,T)
3. t2 = t1 + a   // t2 in [0, 2T)
4. t2 = t2 + a   // t2 in [0, 4T)
5. t3 = b * b    // t3 in [0, T)
6. t2 = red(T2)  // t2 in [0, T)
7. t4 = t2 - t3  // t4 in [0, T]
8. t4 = red(t4)  // t4 in [0, T]
9. 0 = t4 - c
```

In the 8. row prover reduces `t4` into the `[0, T)` range however then this value is compared to an integer in `[0, p)` range comes from a public input. So even if prover can pass the reduction step with `[0, T)` ranged value they actually have to reduce this `t4` intermediate to `[0, p)` range to make the comparison check pass.