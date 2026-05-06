# Chapter 9 — Spectral Prime Geometry: Edges, Energy, and Pseudorandomness

*Prime Geometry in the Binary Hypercube — Part 9*

---

We have now asked two kinds of pseudorandomness questions about primes in the odd hypercube:

- **Geometric**: are prime counts in Hamming balls close to the random-set expectation? (Chapter 7)
- **Algebraic**: do primes have small low-degree Walsh-Fourier coefficients? (Chapter 8)

In this chapter we take the third angle: **spectral and graph-theoretic**. We treat the odd subcube as a graph — vertices are integers, edges connect pairs that differ in exactly one bit — and ask: does the set of prime vertices look like a random independent set in this graph, or does it have unexpected structure?

---

## The odd subcube as a graph

The odd hypercube Q_m^odd has:

- **Vertices:** all odd integers in [1, 2^m − 1], a set of size 2^(m−1)
- **Edges:** pairs (x, y) with d_H(x, y) = 1 and both x, y odd

Since flipping bit 0 toggles parity, and we restrict to odd vertices, only bits 1 through m−1 can be flipped while staying in Q_m^odd. So each vertex has degree m−1 (one neighbor per free bit).

The total number of edges is:

```
|E(Q_m^odd)| = (m−1) · 2^(m−2)
```

The odd subcube is a (m−1)-regular bipartite graph (the bipartition comes from the Hamming weight of bits 1…m−1 being even or odd).

---

## Prime-prime edges

Define the **prime-prime edge count**:

```
E_1 = |{ (p, q) : p, q ∈ P_m, d_H(p, q) = 1 }|
```

This counts how many pairs of prime vertices are Hamming-1 neighbors.

Under the null model — if primes were a uniform random subset of Q_m^odd with density δ_m — the expected prime-prime edge count would be:

```
E[E_1] ≈ δ_m² · |E(Q_m^odd)| = δ_m² · (m−1) · 2^(m−2)
```

because each edge independently has probability δ_m² of having both endpoints prime.

The ratio:

```
ρ = E_1 / E[E_1]
```

measures whether primes are more (ρ > 1) or less (ρ < 1) connected in the Hamming graph than a random subset of the same density.

- **ρ > 1**: primes cluster — prime vertices are Hamming-close to each other more than random
- **ρ < 1**: primes repel — prime vertices are spread out, with fewer edges between them
- **ρ ≈ 1**: primes look like a random graph-subset

---

## The spectral adjacency energy

The graph-theoretic quantity that unifies the edge-count view is the **spectral adjacency energy**:

```
f^T A f
```

where A is the adjacency matrix of Q_m^odd and f is the prime indicator vector.

Expanding:

```
f^T A f = ∑_{(x,y) ∈ E} 2 · f(x) · f(y) = 2 · E_1
```

So measuring f^T A f is equivalent to counting prime-prime edges. But the spectral framing makes it easy to generalize:

- **f^T A^2 f**: counts prime-prime walks of length 2 (i.e., triples p, q, r where p−q and q−r differ in one bit each, and p, r are both prime)
- **f^T A^k f**: counts prime-prime walks of length k

Higher powers probe longer-range connectivity: are primes arranged in chains, clusters, or spread uniformly across the graph?

---

## Edge counts by bit position

We can decompose E_1 by the bit position being flipped:

```
E_1^{(j)} = |{ (p, q) : p, q prime, q = p XOR 2^j }|
```

The total E_1 = ∑_{j=1}^{m−1} E_1^{(j)}.

Under the random model, each E_1^{(j)} should be approximately:

```
δ_m² · 2^(m−2)
```

If a particular bit position j shows a significantly elevated ratio E_1^{(j)} / E[E_1^{(j)}], that means **flipping bit j is unusually likely to take you from a prime to another prime**. This would be a very strong structural signal — a kind of "prime number highway" along bit j.

We measure this for all j = 1, …, m−1 and plot the ratios.

---

## What the experiments show

Running the edge-count experiment for m = 10, 12, 14, 16:

**Overall ratio ρ:** Across all tested dimensions, ρ sits consistently around **0.67** — primes have roughly one-third fewer Hamming-1 connections than a random set of the same density would produce.

| m | Prime-prime edges | Expected (random) | Ratio ρ |
|---|---|---|---|
| 10 | 171 | 257 | 0.67 |
| 12 | 590 | 851 | 0.69 |
| 14 | 1,931 | 2,861 | 0.67 |
| 16 | 6,494 | 9,793 | 0.66 |

**By bit position:** Strikingly, the ratio is nearly **uniform across all bit positions** — about 0.67 for bit 1 (step = ±2) through bit m−1 (step = ±2^(m−2)). There is no strong gradient favoring low or high bit positions.

**Comparison to random baseline:** The random prime-like set produces ρ ≈ 1.0 for all bit positions, confirming the deviation is a genuine number-theoretic signal rather than an artifact of the measurement.

---

## Why primes repel in Hamming-1 space

The ρ ≈ 0.67 result is not an error — it reflects a classical number-theoretic phenomenon: **sieve cancellation**.

The random-model baseline assumes that if p is prime, the probability that p ± 2^j is also prime is independently δ_m. But this independence is broken by modular arithmetic.

Consider the simplest case — bit 1, step ±2 (twin primes). For primes p > 3:
- p is either ≡ 1 or ≡ 2 (mod 3)
- If p ≡ 1 (mod 3), then p + 2 ≡ 0 (mod 3) — divisible by 3, cannot be prime
- If p ≡ 2 (mod 3), then p + 2 ≡ 1 (mod 3) — could be prime

About half of primes > 3 fall in each class, so roughly half of all "flipping bit 1" moves from a prime are immediately blocked by divisibility by 3. Similar sieve obstructions apply for each step size 2^j and each small prime.

The Hardy-Littlewood twin prime conjecture says that these sieve corrections reduce the twin prime count by a multiplicative factor C₂ ≈ 0.66 relative to the naive density-squared prediction — strikingly close to the ρ ≈ 0.67 we observe empirically.

**The uniform ratio across all bit positions** is a deeper observation: regardless of the step size 2^j (which ranges from 2 to 2^(m−2)), the sieve correction factor stays near 0.67. This suggests the dominant sieve effect — the mod-3 blocking — is nearly bit-position-independent, which makes sense since the step 2^j is always divisible by 2 and has no fixed divisibility by 3.

So the spectral edge experiment is picking up a real, classical result — primes repel each other in Hamming-1 neighborhoods — and the magnitude matches the Hardy-Littlewood constant C₂ ≈ 0.66.

---

## Running the experiments

```bash
# Edge counts by bit position
python scripts/run_prime_edge_counts.py --ms 14 16 18 20

# Full comparison including spectral energy
python scripts/run_random_baseline_comparison.py --ms 16 18 20 --radii 1 2 3 4
```

Output:

- `results/raw/prime_edge_counts.csv` — one row per (m, bit_position, source)
- `results/summaries/prime_edge_counts_summary.csv` — total edges and ratio per m
- `results/plots/edge_counts/` — bar charts of edge ratio by bit

---

## Synthesizing all three pseudorandomness views

We have now run three complementary pseudorandomness experiments on the prime set in the odd hypercube:

| Experiment | Question | Result |
|---|---|---|
| Hamming-ball discrepancy (Ch. 7) | Are prime counts in balls close to random? | Yes — z-scores near N(0,1) |
| Walsh-Fourier coefficients (Ch. 8) | Do primes correlate with parity patterns? | No — all low-degree coefficients are small |
| Hamming-1 edge counts (Ch. 9) | Are prime vertices unusually well-connected? | No — ρ ≈ 0.67, primes repel (sieve effect ≈ C₂) |

The three views tell a nuanced story:

> **At the Hamming-ball scale, prime counts fluctuate like a random set (z-scores near normal). At the single-edge scale, primes have significantly fewer connections than random — reflecting the sieve repulsion captured by the Hardy-Littlewood constant C₂ ≈ 0.66. And in Fourier space, primes show no detectable low-degree parity correlations.**

These results are not contradictory. Hamming balls at radius ≥ 2 contain enough vertices that sieve effects average out; Hamming-1 edges are sharp enough to detect the sieve repulsion directly.

This is the hypercube-geometry version of the classical prime pseudorandomness theme — the same intuition that underlies the Riemann Hypothesis, expressed in binary combinatorial geometry.

---

## What this series has covered

Looking back across all nine chapters:

1. **The hypercube model** — primes as vertices, Hamming distance as metric
2. **Distance to the nearest prime** — density and Hamming-ball coverage
3. **Directional bias** — bit-position asymmetry in successful search paths
4. **Learned search policies** — using observed flip paths to build a better search order
5. **Odd subcube vs standard comparison** — why the odd subcube is the right comparison basis
6. **Pareto geometry** — neither low-Hamming nor fast-check strategies dominate on both axes
7. **Prime discrepancy in Hamming balls** — geometric pseudorandomness
8. **Walsh-Fourier view** — algebraic pseudorandomness
9. **Spectral edge geometry** — graph-theoretic pseudorandomness and the twin prime signature

The journey started with a practical question about prime search and ended at the doorstep of some of the deepest open questions in number theory — approached from an unexpected direction.

The code for all experiments is at [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search).
