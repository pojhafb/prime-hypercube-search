# Chapter 10 — XOR Autocorrelation: The Sieve Fingerprint in Hypercube Geometry

*Prime Geometry in the Binary Hypercube — Part 10*

---

In Chapter 9 we found that prime-prime Hamming-1 edges are roughly one-third fewer than a random subset would produce — ρ ≈ 0.664, stable across m = 10–22. That was the single-bit-flip picture.

This chapter asks the natural generalisation: what happens at two bit flips? Three? Four? Eight?

The answer is a clean mathematical pattern that connects hypercube geometry, XOR group structure, and sieve theory in a single formula.

---

## The object: XOR autocorrelation

For any XOR mask a, define:

```
C(a) = |{ p ∈ P_m : p XOR a ∈ P_m }|
```

This counts prime pairs (p, q) whose XOR is exactly a — equivalently, pairs that differ in precisely the bit positions where a has a 1.

Special cases:
- a = 2^j (single bit j): C(a) counts Hamming-1 prime-prime edges along bit j. This is what Chapter 9 measured.
- popcount(a) = 2: C(a) counts prime pairs at Hamming distance 2 with that specific two-bit pattern.
- General a: C(a) gives the full XOR difference distribution of primes.

The natural comparison is the random-model expectation:

```
E[C(a)] ≈ δ_m² × |Q_m^odd| = δ_m² × 2^(m−1)
```

And the ratio:

```
ρ(a) = C(a) / E[C(a)]
```

measures whether prime pairs at XOR distance a are more (ρ > 1) or less (ρ < 1) common than random.

---

## Computing C(a) efficiently

A naive computation would check all prime pairs — O(|P_m|²), which is prohibitive for large m.

The fast path uses the **Walsh-Hadamard Transform (WHT)**. The XOR autocorrelation is a XOR convolution, and convolution becomes pointwise multiplication in the Walsh-Fourier domain:

```
C = IWHT( WHT(f)² )
```

where f is the prime indicator vector on all 2^m integers. This runs in O(m × 2^m) time — the same cost as building the prime set itself.

For m = 20: 20 × 2^20 ≈ 20 million operations. The full C(a) array for all 2^20 masks computes in under a second.

---

## The pattern: weights 1 through 8

Running the experiment at m = 18 and m = 20 for all even masks (bit 0 not flipped) of Hamming weight 1 through 8:

| Weight | ρ (m=20) | σ vs random | Pattern |
|---|---|---|---|
| 1 | 0.662 | −28σ | **repulsion** |
| 2 | 1.139 | +12σ | **excess** |
| 3 | 0.938 | −5σ | repulsion (weaker) |
| 4 | 1.036 | +3σ | excess (weaker) |
| 5 | 0.986 | −1σ | ≈ random |
| 6 | 1.011 | +1σ | ≈ random |
| 7 | 0.997 | <1σ | indistinguishable |
| 8 | 1.004 | <1σ | indistinguishable |

Two things are immediately visible:

**1. Sign alternation by weight parity.** Odd Hamming weights give ρ < 1 (prime pairs are rarer than random). Even Hamming weights give ρ > 1 (prime pairs are more common than random). This holds cleanly for weights 1–4 and fades by weight 5–6.

**2. Geometric decay.** The deviation |ρ − 1| shrinks by roughly a factor of 2.2 at each weight step. By weight 5, the signal has decayed below 1σ noise. By weight 7–8 primes are indistinguishable from random in XOR geometry.

---

## The model

The pattern fits a single parametric formula:

```
ρ(k) = 1 + C₀ × (−r)^k
```

where k is the Hamming weight of the mask, C₀ ≈ 0.70, and r ≈ 0.46.

Fitting this model to the m = 20 data (log-linear least squares on weights 1–5):

```
ρ(k) = 1 + 0.699 × (−0.459)^k
```

| Weight | Observed | Predicted | Residual |
|---|---|---|---|
| 1 | 0.6624 | 0.6789 | −0.016 |
| 2 | 1.1393 | 1.1473 | −0.008 |
| 3 | 0.9382 | 0.9324 | +0.006 |
| 4 | 1.0358 | 1.0311 | +0.005 |
| 5 | 0.9864 | 0.9857 | +0.001 |
| 6 | 1.0111 | 1.0065 | +0.005 |
| 7 | 0.9966 | 0.9970 | −0.000 |
| 8 | 1.0038 | 1.0014 | +0.002 |

RMSE < 0.02 across all 8 weights. The model captures both the alternation and the decay accurately.

The two parameters carry distinct meanings:
- **r ≈ 0.46**: the amplitude of the correction halves (roughly) at each additional bit flip. This is the decay rate of the sieve fingerprint.
- **−r**: the sign flip at each weight level. Odd weights repel, even weights attract.
- **C₀ ≈ 0.70**: the strength of the weight-1 correction. Note that 1 − C₀ × r ≈ 1 − 0.32 = 0.68, consistent with the observed ρ(1) ≈ 0.664 and the Hardy–Littlewood constant C₂ ≈ 0.66.

---

## Why the sign alternates: inclusion-exclusion of sieve obstructions

The alternating sign is not coincidental. It reflects **inclusion-exclusion in the sieve**.

For a weight-1 mask a = 2^j, the prime pair (p, p XOR a) suffers a modular obstruction: for roughly half of all primes p, divisibility by 3 forces p XOR 2^j to be composite. This drives ρ below 1.

For a weight-2 mask a = 2^j + 2^k, the pair (p, p XOR a) flips two bits simultaneously. The two modular obstructions — one from each bit flip — partially **cancel**. Flipping bit j might make p XOR 2^j divisible by 3, but flipping bit k as well changes the residue again, partly undoing the obstruction. The net effect at weight 2 is excess rather than deficit.

At weight 3, three obstructions enter, and the net sign flips again. At weight 4, four. This is exactly the inclusion-exclusion structure of the Möbius function in sieve theory:

```
μ(p₁ p₂ … pₖ) = (−1)^k
```

The alternating correction ρ(k) ≈ 1 + C₀ (−r)^k mirrors this Möbius alternation, with r encoding the typical size of a single sieve correction factor.

This is a heuristic argument, not a proof. But the data fits it precisely across 8 weight levels and two values of m.

---

## Which weight-2 masks have highest ρ?

The weight-2 excess is not uniform — some two-bit pairs connect primes far more often than others.

At m = 18, the top weight-2 masks by ρ are consistently pairs with **bit-position difference = 12**:

```
(1, 13)  →  ρ = 1.527
(2, 14)  →  ρ = 1.551
(3, 15)  →  ρ = 1.527
(4, 16)  →  ρ = 1.532
(5, 17)  →  ρ = 1.500
```

Why 12? Because 2^12 ≡ 1 (mod 3), 2^12 ≡ 1 (mod 5), 2^12 ≡ 1 (mod 7). So 2^12 − 1 = 4095 = 3² × 5 × 7 × 13, and flipping a bit at position j and at position j+12 leaves the integer's residues modulo 3, 5, and 7 unchanged when the XOR value is viewed as 2^j(1 + 2^12). The sieve obstructions are systematically reduced for these "period-12" pairs.

The mod-3 grouping confirms it: weight-2 masks with mask ≢ 0 (mod 3) have ρ ≈ 1.23, while masks ≡ 0 (mod 3) have ρ ≈ 1.05. When the mask itself is not divisible by 3, the pair (p, p XOR mask) is not blocked by the mod-3 sieve, and the excess is larger.

---

## The prime-induced graph

Alongside the XOR autocorrelation, we also built the **prime-induced subgraph** G_m^prime: vertices are primes in Q_m^odd, edges connect pairs at Hamming distance 1.

| m | Primes | Edges | Components | Largest (%) | Isolated (%) | Avg degree |
|---|---|---|---|---|---|---|
| 12 | 563 | 590 | 58 | 81.5% | 7.3% | 2.10 |
| 14 | 1,899 | 1,931 | 218 | 78.1% | 8.9% | 2.03 |
| 16 | 6,541 | 6,494 | 875 | 73.7% | 10.9% | 1.99 |
| 18 | 22,999 | 22,721 | 3,236 | 71.4% | 11.6% | 1.98 |

Compared to a random subset of the same density, which would have:
- Largest component ≈ 95% of vertices
- Isolated fraction ≈ 4%
- ~3× fewer components

The prime-induced graph is significantly **more fragmented** than random — entirely consistent with the ρ ≈ 0.664 edge deficit. Fewer edges means more disconnected pieces, more isolated primes, and a smaller giant component.

The giant component still covers 71–82% of primes, so most primes are reachable from most others via Hamming-1 hops. But the gap versus random (~95%) is many standard deviations wide and widens as m grows, consistent with a graph that is sub-critical relative to the random connectivity threshold.

---

## The complete picture: a scale-dependent sieve fingerprint

Putting Chapters 7–10 together, the XOR autocorrelation C(a) reveals a three-regime structure:

**Regime 1: single bit flips (weight 1)**
ρ ≈ 0.664, consistent across all m and all bit positions. Strong sieve repulsion. The Hardy–Littlewood constant C₂ ≈ 0.66 appears directly.

**Regime 2: two to four bit flips (weights 2–4)**
ρ alternates above and below 1, with amplitude decaying geometrically. Statistically significant (3–12σ). Reflects inclusion-exclusion of sieve corrections. Specific mask geometry matters — bit-position difference = 12 gives maximum excess at weight 2.

**Regime 3: five or more bit flips (weights 5+)**
ρ ≈ 1.000 within ≤ 1σ. Primes are statistically indistinguishable from a random subset. The sieve fingerprint has fully decayed.

The model `ρ(k) = 1 + C₀(−r)^k` with C₀ ≈ 0.70, r ≈ 0.46 captures all three regimes in a single formula. The sieve fingerprint is detectable for exactly 4 bit flips and disappears thereafter.

This is the deepest result of the series: the XOR geometry of primes carries a **measurable, structured, exponentially-decaying sieve fingerprint** that is visible to exactly depth 4 in the hypercube, and random beyond that.

---

## Running the experiment

```bash
cd prime-hypercube-search

# XOR autocorrelation weights 1-8 with model fit
python scripts/run_xor_autocorr.py --ms 18 20 --max-weight 8 --n-baselines 10

# Prime-induced graph connectivity
python scripts/run_prime_graph.py --ms 12 14 16 18 --n-baselines 10
```

Output:
- `results/raw/xor_autocorr.csv` — one row per (m, mask)
- `results/summaries/xor_autocorr_by_weight.csv` — mean ρ by weight and m
- `results/summaries/xor_model_fit_m{m}.csv` — model predictions vs observed
- `results/plots/xor_autocorr/` — ρ by weight, histogram, mod groupings, model fit curve
- `results/summaries/prime_graph_summary.csv` — connectivity metrics by m

---

## What comes next

The alternating model `ρ(k) = 1 + C₀(−r)^k` is empirical. Three natural next questions:

1. **Is r = C₂^(1/k_0) for some natural k₀?** The decay factor r ≈ 0.46 should be derivable from the Hardy–Littlewood singular series and the sieve structure of XOR pairs.

2. **Does the weight-2 maximum at bit-difference = 12 generalise?** For other m values, do the top weight-2 masks always have bit-difference = ord₃₅₇(2) = 12? Or does the pattern shift?

3. **What is the Fourier interpretation?** The model ρ(k) is a function of Hamming weight only (to leading order). Hamming-weight-symmetric functions on the hypercube correspond to zonal spherical functions. The alternating geometric model may have a clean eigenvalue interpretation in the hypercube spectrum.

All code is at [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search).
