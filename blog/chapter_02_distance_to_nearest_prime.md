# Chapter 2: How Far Is a Number from a Prime?

*Prime Geometry in the Binary Hypercube — Part 2*

---

In Chapter 1, we set up the question: are primes sparse in Hamming geometry the
same way they are sparse on the number line?

Here we measure it directly.

---

## The experiment

For $m = 14$ we have $2^{14} = 16384$ integers. We ran a complete scan — every
integer from 0 to 16383 — and for each one, found the nearest prime in Hamming distance.

Formally, for each $x$ we compute:

$$D_m(x) = \min_{p \in P_m} d_H(x, p)$$

where $P_m$ is the set of primes in $Q_m$ and $d_H$ is Hamming distance.

We searched up to Hamming radius 4. Any integer not resolved within radius 4 was
flagged as unresolved.

---

## The result

| Hamming distance to nearest prime | Count | Percentage |
|----------------------------------:|------:|-----------:|
| 0 | 1900 | 11.6% |
| 1 | 7933 | 48.4% |
| 2 | 6286 | 38.4% |
| 3 | 265 | 1.6% |
| unresolved at radius 4 | 0 | 0.0% |

Every single integer in $Q_{14}$ is within Hamming distance 3 of a prime.
About 98% are within distance 2.

---

## Why this happens

The result follows from a combinatorial argument.

The number of primes up to $N = 2^{14} = 16384$ is approximately:

$$\pi(N) \approx \frac{N}{\ln N} \approx \frac{16384}{9.7} \approx 1688$$

(The exact count is 1900 primes in $[0, 16383]$, consistent with this estimate.)

The Hamming ball of radius 2 around any $m=14$ vertex contains:

$$B(14, 2) = \binom{14}{0} + \binom{14}{1} + \binom{14}{2} = 1 + 14 + 91 = 106 \text{ vertices}$$

With roughly $\frac{1900}{16384} \approx 11.6\%$ of vertices being prime, the
expected number of primes within radius 2 is about $106 \times 0.116 \approx 12$.

So the radius-2 ball almost always contains a prime. Distance 3 cases are the
rare exceptions where the local neighborhood happens to be prime-thin.

---

## What about larger m?

We also sampled from $m = 16, 18, 20$ (20,000 random samples each).
The pattern persists: almost all sampled integers are within Hamming distance 2
of a prime.

As $m$ grows:
- Prime density drops as $\frac{1}{m \log 2}$
- But the Hamming ball grows much faster — $B(m, 2) = 1 + m + \binom{m}{2}$

The ball grows quadratically in $m$. The density drops linearly. So the expected
primes in a radius-2 ball actually *increases* with $m$.

This is the first key finding:

> **Primes are sparse on the number line, but nearly every integer has a prime
> within just a few bit flips.**

---

## The follow-up question

The finding above says primes are close in Hamming space. But it does not say
anything about which bit flips get us there fastest.

If you flip bit 0, you toggle parity — you turn an even number odd (or vice versa).
All primes greater than 2 are odd. So flipping bit 0 has an obvious advantage.

Does this mean bit 0 drives everything? And what happens if we remove that advantage?

That is the subject of Chapter 3.

---

## Reproducing this result

```bash
python scripts/run_distance_distribution.py
```

Output is saved to `results/summaries/distance_dist_m14_full.csv`.

---

*Code: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
