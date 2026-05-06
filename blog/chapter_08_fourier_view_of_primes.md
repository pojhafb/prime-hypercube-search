# Chapter 8 — The Fourier View of Prime Geometry

*Prime Geometry in the Binary Hypercube — Part 8*

---

In the last chapter we tested whether primes are geometrically random in the odd hypercube — are prime counts in Hamming balls close to what a random set would produce? The answer was: yes, at least at the scales we could test.

But geometry is only one lens. In this chapter we look through an algebraic one: **Walsh-Fourier analysis**.

The question becomes: do primes correlate with simple parity patterns on the bits? Can a low-degree "bit formula" pick out prime vertices better than chance?

---

## The Boolean Fourier toolkit

Every function on the hypercube {0,1}^m can be written as a multilinear polynomial over the reals. The natural basis for this expansion consists of **parity functions**, also called Walsh characters or Fourier-Walsh characters.

For a subset S ⊆ {1, 2, …, m−1} of bit positions (we exclude bit 0 since we work in the odd subcube), define:

```
χ_S(x) = (−1)^{ popcount(x AND mask_S) }
```

where mask_S has 1s in exactly the positions in S. This function is +1 if the bits in S have even parity, and −1 if they have odd parity.

The **Walsh-Fourier expansion** of any function g: Q_m^odd → ℝ is:

```
g(x) = ∑_{S ⊆ [m−1]}  ĝ(S) · χ_S(x)
```

where the coefficient is:

```
ĝ(S) = (1/N) · ∑_x  g(x) · χ_S(x)
```

and N = |Q_m^odd| = 2^(m−1).

The **degree** of a coefficient is |S|.

---

## The prime indicator and centering

Define the prime indicator function:

```
f(x) = 1  if x is prime
f(x) = 0  otherwise
```

We center it by subtracting the density:

```
g(x) = f(x) − δ_m
```

The degree-0 coefficient is ĝ(∅) = 0 by construction (centering removes the constant).

A large |ĝ(S)| for a small set S would mean: **primes correlate strongly with the parity of bits in S**. In other words, a simple k-bit formula distinguishes prime vertices from non-prime vertices better than random chance.

A "pseudorandom" prime indicator would have **all low-degree coefficients close to zero** — primes do not cluster according to simple parity rules.

---

## What degree means

- **Degree 1** (|S| = 1): primes correlate with single bit being 0 or 1. 
  - Example: primes are more likely when bit 5 is 0.
  - This would be a very simple structural bias.
  
- **Degree 2** (|S| = 2): primes correlate with parity of two bits.
  - Example: bit 3 XOR bit 7 = 0 among primes more often than random.
  
- **Degree 3** (|S| = 3): three-way parity correlations.

Classical results in analytic number theory (e.g., prime equidistribution in arithmetic progressions) imply that degree-1 Fourier coefficients corresponding to bit-position conditions should be very small — primes are not systematically concentrated in "bit k = 1" versus "bit k = 0" subcubes. This is essentially the content of the Prime Number Theorem for arithmetic progressions.

---

## Connection to arithmetic progressions

Fixing the last k bits of a binary integer is equivalent to fixing its value modulo 2^k. So:

- A degree-1 condition on bit position j fixes x mod 2^(j+1) to be in {2^j, 2^j + 1, …, 2^(j+1) − 1} (or the complementary set).
- This corresponds to a union of residue classes modulo 2^(j+1).

Prime distribution across these residue classes is governed by Dirichlet's theorem and the Prime Number Theorem for arithmetic progressions. Under the Generalized Riemann Hypothesis, the error terms are small — which would imply small degree-1 Fourier coefficients.

So the Fourier view connects naturally to classical results.

---

## What the experiments show

Running the Walsh-Fourier analysis for m = 12, 14, 16 with max degree 3:

**Degree-0:** ĝ(∅) = 0 exactly (by centering construction).

**Degree-1 coefficients:** All are very small — on the order of 10^(−4) to 10^(−3). There is no single bit position whose 0/1 value strongly predicts primality after accounting for overall density. This is expected from the PNT for arithmetic progressions.

**Degree-2 coefficients:** Again small, but slightly larger in magnitude than degree-1. The largest degree-2 coefficients tend to involve adjacent or nearby bit positions. This is consistent with the fact that nearby bits jointly encode congruence class information, and primes avoid certain congruence classes (e.g., multiples of 3, 5, etc.).

**Degree-3 coefficients:** The largest absolute values in the top-30 list tend to be degree-2 or degree-3. But all are well below 0.01 for m ≥ 14.

**Comparison to random baseline:** A random subset of the same density produces similarly sized coefficients — there is no clear separation between the prime Fourier spectrum and the random Fourier spectrum at these degrees.

The takeaway: **the prime indicator function has very small low-degree Walsh-Fourier coefficients**, consistent with prime pseudorandomness in binary parity geometry.

---

## Parseval's identity and spectral energy

Parseval's identity on the Boolean hypercube says:

```
∑_S  ĝ(S)² = Var(g) = δ_m · (1 − δ_m)
```

The fraction of variance explained by degree-d coefficients is:

```
W^{≤d} = ∑_{|S| ≤ d}  ĝ(S)² / Var(g)
```

For a pseudorandom function, most variance lives at high degree (large S). If W^{≤3} is small compared to the total variance, primes do not "look simple" to low-degree Fourier tests.

In our experiments, W^{≤3} / Var(g) is well under 5% for m ≥ 14, and it shrinks as m grows. High-degree (complex, many-bit) structure accounts for almost all the variance in the prime indicator. This is consistent with the view that primality is a "high-complexity" Boolean function.

---

## Running the experiment

```bash
cd prime-hypercube-search
python scripts/run_fourier_prime_indicator.py --ms 12 14 16 --max-degree 3 --top-n 30
```

Output:

- `results/raw/fourier_m{m}_deg3.csv` — all coefficients up to degree 3
- `results/plots/fourier/` — bar charts of top-N coefficients by degree

For m > 16, the experiment becomes slow (2^(m−1) vertices × number of subsets). The code enforces a limit of m ≤ 20.

---

## Limitations

The Fourier approach here is **exact but computationally limited to small m**. For m = 20, the odd subcube has 2^19 ≈ 500,000 vertices and the number of subsets up to degree 3 is C(19,0) + C(19,1) + C(19,2) + C(19,3) ≈ 1,142 — manageable.

For m = 32 (our search experiments), the full Fourier computation is infeasible without approximation. Randomized Fourier sampling (learning Fourier coefficients via random linear combinations) is possible but beyond the current scope.

The experiments establish the qualitative picture at moderate m: primes look Fourier-pseudorandom to low-degree tests.

---

## What's next

We have looked at geometric pseudorandomness (Hamming balls) and algebraic pseudorandomness (Fourier coefficients). One more structural view remains: the **graph / spectral perspective**.

Do prime vertices in the odd hypercube form a well-connected, spread-out graph? Or do they cluster into dense components with sparse edges between components? That is the subject of Chapter 9.
