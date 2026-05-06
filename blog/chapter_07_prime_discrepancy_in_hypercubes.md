# Chapter 7 — Prime Discrepancy in the Binary Hypercube

*Prime Geometry in the Binary Hypercube — Part 7*

---

In the first six chapters we asked: **how do you find the next prime from a given starting point in the odd hypercube?** We compared search strategies, studied directional bias, built learned policies, and traced out Pareto frontiers between speed and locality.

Now we shift the question.

Instead of asking how hard it is to *find* a prime, we ask something deeper: **are primes distributed randomly inside the hypercube, or do they form clusters, voids, and patterns that deviate from pure chance?**

This is the hypercube version of a question that sits at the heart of analytic number theory — and at the edge of the Riemann Hypothesis.

---

## The classical picture

In classical prime number theory, the gold-standard question about prime distribution is:

> How close is π(x) — the count of primes up to x — to Li(x), the logarithmic integral?

The Prime Number Theorem tells us that π(x) ~ Li(x). The Riemann Hypothesis, if true, would sharpen this to say the error |π(x) − Li(x)| is bounded by roughly √x · log(x) — a "square-root cancellation" that would mean primes are about as regularly distributed as possible given their density.

We cannot test RH directly in our finite experiments. But we can ask a structurally analogous question in the binary hypercube.

---

## The hypercube framing

Fix a dimension m. Consider the odd subcube:

```
Q_m^odd = { x ∈ {0,1}^m : bit 0 = 1 }
```

which has 2^(m−1) vertices. Among these, the prime vertices are:

```
P_m = { x ∈ Q_m^odd : x is prime }
```

The density of primes in the odd subcube is approximately:

```
δ_m ≈ 2 / (m · ln 2)
```

This follows from the Prime Number Theorem: among odd integers near 2^(m−1), about 1 in (m−1)·ln(2) are prime.

Now pick any vertex x and a Hamming radius r. The Hamming ball is:

```
B(x, r) = { y ∈ Q_m^odd : d_H(x, y) ≤ r }
```

Its size (in the odd subcube, which has m−1 free bits) is:

```
|B(x, r)| = ∑_{i=0}^{r} C(m−1, i)
```

which grows much faster than an arithmetic interval of the same "reach."

The **prime count discrepancy** inside this ball is:

```
Δ(x, r) = |P_m ∩ B(x, r)| − δ_m · |B(x, r)|
```

And the normalized z-score is:

```
Z(x, r) = Δ(x, r) / sqrt( δ_m · (1 − δ_m) · |B(x, r)| )
```

The denominator is the standard deviation of prime count if primes were a random Bernoulli(δ_m) subset of the subcube.

---

## The key question

If Z(x, r) is approximately N(0, 1) for many sampled centers x, then **primes look like a random subset of the odd hypercube**, at least at the Hamming-ball scale.

If Z(x, r) is systematically positive or negative, or has heavier tails than normal, then **primes are more clustered or more spread out than a random set of the same density**.

This is our hypercube-flavored pseudorandomness test.

---

## The random baseline

To make the comparison concrete, we also create a **random prime-like set**: a randomly chosen subset of Q_m^odd with exactly the same density δ_m, but with no number-theoretic structure.

We then run the same discrepancy calculation on the random set and compare the z-score distributions side by side.

This lets us ask:

> Are the fluctuations of prime counts inside Hamming balls bigger or smaller than what a random subset would produce?

---

## What the experiments show

Running the discrepancy experiment for m = 16, 18, 20 with radii r = 1, 2, 3, 4 and 2,000 sampled centers:

**Z-score histograms:** The prime z-scores are roughly bell-shaped and centered near zero. For small radii (r = 1, 2), where ball sizes are modest, the histograms are slightly wider than N(0,1) — consistent with small-sample variance. For larger radii (r = 3, 4), where balls contain many vertices, the z-scores tighten toward normality.

**Comparison to random baseline:** The random prime-like set produces z-score histograms that are nearly indistinguishable from the prime histograms, at the scale our experiments can resolve.

**Mean discrepancy:** The mean of Δ(x, r) is very close to zero across all m and r values, for both primes and the random baseline.

The upshot: **at the Hamming-ball scale tested here, prime vertices are not detectably more clustered or more spread out than a random subset of the odd hypercube with the same density.**

---

## Connecting to RH

The Riemann Hypothesis implies that prime counting fluctuations on the number line show square-root-level cancellation. Our experiment asks whether the analogous property holds in hypercube geometry.

We are not proving RH, and we are not claiming a new theorem. But the experiment is testing the same intuition: *do primes behave like a pseudorandom set?*

What we observe is consistent with prime pseudorandomness in Hamming-ball geometry. A random subset of the same density is statistically indistinguishable from the real primes, at the resolution our finite experiments can achieve.

---

## Running the experiment yourself

```bash
cd prime-hypercube-search
python scripts/run_hamming_ball_discrepancy.py --ms 16 18 20 --radii 1 2 3 4 --samples 2000
```

Output:

- `results/raw/hamming_ball_discrepancy.csv` — one row per (center, radius, source)
- `results/summaries/hamming_ball_discrepancy_summary.csv` — mean/std z-score per (m, radius, source)
- `results/plots/discrepancy/` — z-score histograms and discrepancy box plots

For the full primes vs random comparison:

```bash
python scripts/run_random_baseline_comparison.py --ms 16 18 20 --radii 1 2 3 4
```

---

## What's next

We have tested pseudorandomness at the *geometric* level — Hamming balls. The next question is whether prime pseudorandomness holds at the *algebraic* level: do primes correlate with simple parity patterns on the bits?

That is the Fourier question, and it is the subject of Chapter 8.
