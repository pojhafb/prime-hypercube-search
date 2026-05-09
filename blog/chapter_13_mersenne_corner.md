# Chapter 13 — The Mersenne Corner

*Prime Geometry in the Binary Hypercube — Part 13*

---

## A special vertex

In the odd binary hypercube Q_m^odd = {1, 3, 5, ..., 2^m − 1}, most prime vertices are scattered throughout. Mersenne primes are different: M_p = 2^p − 1 is the **all-ones vertex** of Q_p, the unique vertex with every bit set to 1.

```
2^7 − 1 = 127  →  1111111
2^31 − 1       →  1111111111111111111111111111111
```

This gives Mersenne primes a geometric identity in hypercube terms: they are **corner primes**, sitting at the maximum-Hamming-weight vertex of their respective cubes. All other odd primes have at most p − 1 ones in binary.

A necessary condition follows cleanly: the all-ones vertex of Q_m can be prime only when m is prime. If m = ab with a, b > 1 then 2^m − 1 = (2^a − 1)(1 + 2^a + 2^{2a} + ... + 2^{(b−1)a}) factors. So Mersenne candidates live only in prime-indexed dimensions.

This chapter asks: **is the neighbourhood of a Mersenne corner unusual?** And: **does the primality of the corner itself affect its neighbourhood**?

---

## The XOR-subtraction identity

For the all-ones vertex x = 2^p − 1 and any mask a < 2^p:

```
x XOR a  =  (2^p − 1) XOR a  =  (2^p − 1) − a
```

because every bit of x is 1, so XOR with a simply flips those bits — which is the same as subtracting a from x. This is the key structural fact:

> **At the Mersenne corner, Hamming moves are exactly arithmetic subtraction of sparse binary masks.**

For generic x this fails: XOR is not subtraction. At the all-ones vertex it is exact.

So the Hamming-r neighbourhood of 2^p − 1 is:

```
B(M_p, r)  =  { M_p − a  :  popcount(a) = r,  bit_0(a) = 0 }
```

(we exclude bit 0 of a to keep candidates odd). These are p-bit numbers obtained by deleting exactly r of the 1s from the all-ones string, at positions other than bit 0.

---

## The experimental design

For each prime exponent p ≤ 127, we compare three groups:

**Group A (Mersenne-prime corner):** p ∈ {3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127} — exponents where 2^p − 1 is prime.

**Group B (Mersenne-composite corner):** prime p ≤ 127 with 2^p − 1 composite — e.g., p ∈ {11, 23, 29, 37, ...}.

**Baseline:** 200 random odd p-bit integers x sampled for each p.

For each (group, p, radius r), we count primes in the Hamming shell:

```
N_p(r)  =  |{ a : popcount(a) = r,  bit_0(a) = 0,  M_p − a prime }|
```

The z-score compares N_p(r) to the distribution of shell prime counts over random odd p-bit centers.

We exclude the center (r = 0) from all comparisons to avoid the trivial advantage when M_p is itself prime.

---

## Finding 1: radius-1 neighbourhoods are prime-poor

The Mersenne corner's nearest neighbours — numbers of the form 2^p − 1 − 2^k — are systematically **fewer prime** than the neighbourhood of a random odd p-bit integer.

| p  | M_p    | r=1 shell | Primes | Random mean | z-score |
|----|--------|-----------|--------|-------------|---------|
| 7  | prime  | 6         | 0      | 2.6         | −1.73   |
| 11 | comp.  | 10        | 1      | 2.7         | −1.06   |
| 13 | prime  | 12        | 1      | 2.9         | −1.07   |
| 17 | prime  | 16        | 2      | 3.0         | −0.55   |
| 19 | prime  | 18        | 1      | 2.6         | −0.88   |
| 23 | comp.  | 22        | 0      | 2.9         | −1.50   |
| 31 | prime  | 30        | 0      | 3.1         | −1.53   |
| 37 | comp.  | 36        | 0      | 2.9         | −1.55   |
| 61 | prime  | 60        | 3      | 2.8         | +0.12   |
| 89 | prime  | 88        | 4      | 2.7         | +0.78   |

Most exponents show z-scores around −1, with only about 0–2 primes in a shell of p − 1 candidates. The random baseline mean is ~2.8 primes regardless of p. The corner has about 1–1.5 fewer primes than a typical odd center.

### Why: the modular sieve argument

For the all-ones corner, M_p − 2^k ≡ 0 (mod q) iff 2^k ≡ M_p (mod q). Since the powers of 2 are periodic mod q with period ord_q(2), each small odd prime q blocks exactly one residue class of k in every period — roughly a 1/ord_q(2) fraction of the shell.

For M_7 = 127:
- q = 3 (ord_3(2) = 2): 127 ≡ 1 (mod 3), so 2^k ≡ 1 (mod 3) when k is even. Blocks k = 2, 4, 6.
- q = 5 (ord_5(2) = 4): 127 ≡ 2 (mod 5), so 2^k ≡ 2 (mod 5) when k ≡ 1 (mod 4). Blocks k = 1, 5.
- q = 7 (ord_7(2) = 3): 127 ≡ 1 (mod 7), so 2^k ≡ 1 (mod 7) when k ≡ 0 (mod 3). Blocks k = 3, 6.

Coverage: {1,2,3,4,5,6} = all of them. M_7's entire radius-1 shell is composite — every single neighbour is divisible by 3, 5, or 7:

| k | M_7 − 2^k | Composite because |
|---|-----------|-------------------|
| 1 | 125 = 5³  | 5 | 125 |
| 2 | 123 = 3×41 | 3 | 123 |
| 3 | 119 = 7×17 | 7 | 119 |
| 4 | 111 = 3×37 | 3 | 111 |
| 5 | 95 = 5×19  | 5 | 95  |
| 6 | 63 = 9×7   | 3, 7 | 63 |

This is not specific to Mersenne primes — it holds for any number whose residues mod 3, 5, 7 conspire to cover the shell under the periodicity of powers of 2.

---

## Finding 2: radius-2 neighbourhoods are slightly prime-rich

At radius 2, the situation reverses:

| p  | M_p    | r=2 shell | Primes | Random mean | z-score |
|----|--------|-----------|--------|-------------|---------|
| 7  | prime  | 15        | 8      | 6.7         | +0.53   |
| 13 | prime  | 66        | 21     | 15.3        | +1.08   |
| 17 | prime  | 120       | 24     | 20.9        | +0.51   |
| 19 | prime  | 153       | 30     | 25.0        | +0.72   |
| 31 | prime  | 435       | 51     | 40.2        | +1.11   |
| 37 | comp.  | 630       | 64     | 49.6        | +1.14   |
| 61 | prime  | 1770      | 106    | 85.1        | +1.06   |
| 89 | prime  | 3828      | 131    | 127.0       | +0.15   |

Z-scores are consistently positive but modest (+0.5 to +1.1), suggesting a slight excess of primes at radius 2. This is the natural complement to the radius-1 deficit: some prime-density "displaced" from r=1 appears at r=2.

The ratio of observed primes to the naive PNT expectation (uniform density 1/(p ln 2)) is consistently 2–2.9× at r=2. This ratio inflates because the PNT baseline underestimates density — some radius-2 candidates reach numbers as small as 2^(p−2), which are shorter and denser in primes. The z-score, which uses the random-center empirical distribution, is the cleaner comparison.

---

## The key null result: no Mersenne corner effect

Across all radii and all tested p, **there is no statistically significant difference between Mersenne-prime corners (Group A) and Mersenne-composite corners (Group B)**. The z-scores of both groups are interleaved, with no systematic offset.

| Group               | Mean z (r=1) | Mean z (r=2) | Mean z (r=3) |
|---------------------|--------------|--------------|--------------|
| Mersenne prime      | −0.79        | +0.59        | −0.43        |
| Mersenne composite  | −0.99        | +0.52        | −0.52        |

(Computed over p ∈ {7,...,89} with p ≥ 7 and p prime.)

Both groups have r=1 z-scores averaging around −0.9, and r=2 z-scores averaging around +0.5. The difference between groups is well within noise.

**Interpretation:** the all-ones corner has an unusual neighbourhood structure — prime-poor at r=1, slightly prime-rich at r=2 — but this structure is determined entirely by the modular arithmetic of 2^p − 1, not by whether 2^p − 1 is itself prime. The primality of the center is invisible to its neighbours' prime density.

This is Finding C from the professor's suggested experiment:

> After controlling for bit length, shell size, and random odd-center baselines, Mersenne-prime corners are **not** more prime-rich than Mersenne-composite corners.

---

## The XOR singular series interpretation

This result connects directly to the XOR singular series developed in Chapters 10–12.

For a radius-1 mask 2^k, the XOR singular series predicts:

```
ρ(2^k)  →  C₂  ≈  0.664    (averaged over all prime centers)
```

The Mersenne center sits at a special vertex where the local sieve is harsher than average: residue coverage by small primes blocks more shell members than a typical odd center would experience. The radius-1 prime count is not just below the random baseline — it is below even the XOR-autocorrelation prediction, which is itself already 34% below the random-pair expectation.

Put differently: the all-ones corner is an extreme case in the XOR geometry. It sits at maximum Hamming distance from zero and has a very structured modular fingerprint. The XOR singular series characterises the average over all prime centers; the Mersenne corner is an outlier at the edge of that distribution.

---

## What this tells us (and doesn't)

**What it tells us:**
- The all-ones vertex has a well-understood, sieve-governed neighbourhood structure.
- At radius 1, the modular coverage argument predicts prime poverty and the experiment confirms it.
- The primality of the corner itself does not predict whether its neighbourhood is unusual.
- This is consistent with the general XOR-singular-series picture: prime pair density is governed by the sieve factorisation of the mask, not by special properties of individual prime vertices.

**What it does not tell us:**
- Whether larger Mersenne primes (p = 521, 607, ...) show the same pattern. For those, the r=3 shell would have millions of candidates and require a sampling approach.
- Whether the radius-1 prime count for the Mersenne corner has a clean closed form. The sieve argument bounds it from above; computing the exact expected count requires a product of local factors specific to the all-ones residue structure.
- Whether the slight radius-2 excess (z ≈ +0.5 to +1.1) survives at larger p. The current data is consistent with noise.

---

## Summary

| Finding | Status |
|---------|--------|
| M_p = 2^p − 1 is the all-ones vertex of Q_p | Exact |
| M_p XOR a = M_p − a for any mask a < 2^p | Exact |
| Radius-1 neighbourhood is prime-poor (z ≈ −1) | Empirical, p ≤ 127 |
| Sieve explanation: modular coverage blocks shell | Analytic |
| Radius-2 neighbourhood is slightly prime-rich (z ≈ +0.5) | Empirical, moderate |
| No difference between Mersenne-prime and composite corners | Empirical, p ≤ 127 |
| Primality of center does not predict neighbourhood density | Empirical |

All code at [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search).
