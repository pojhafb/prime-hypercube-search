# Chapter 6: Two Geometries of Prime Search

*Prime Geometry in the Binary Hypercube — Part 6*

---

Chapter 5 showed that standard odd-increment search and odd-subcube Hamming search
each win on a large fraction of individual starting points. Neither is uniformly
better. This chapter makes that tension precise using Pareto analysis — and argues
that the right conclusion is not a ranking, but a recognition that prime search
has two natural geometries.

---

## Three metrics

Every search result can be measured on three axes:

**1. Candidate checks** — how many primality tests were performed.
This measures computational cost.

**2. Hamming distance** $d_H(x, p)$ — how many bits differ between the starting
point and the found prime.
This measures bit-space locality.

**3. Arithmetic distance** $|p - x|$ — how far the found prime is on the number line.
This measures number-line locality.

A strategy that minimizes all three simultaneously would be ideal. But no such
strategy exists — the two distance measures conflict.

---

## The Pareto frontier: checks vs. Hamming distance

A strategy is on the **Pareto frontier** for (checks, Hamming distance) if no
other strategy achieves both fewer checks and smaller Hamming distance.

Experimentally, the Pareto frontier for (avg checks, avg Hamming distance) includes:

- **standard_odd_increment**: fewest checks, but largest Hamming distance.
- **low_bit_first_no_bit0**: moderate checks, smallest Hamming distance.
- Sometimes **learned_bit_order**: sits between the two on both axes.

This means both strategies are genuinely useful — neither dominates on both metrics.
The Pareto frontier is not a single point; it is a curve.

If you only care about checks: use standard.
If you only care about Hamming locality: use low-bit-first.
If you care about both: you face a real tradeoff.

---

## The Pareto frontier: checks vs. arithmetic distance

For (avg checks, avg arithmetic distance):

- **standard_odd_increment** dominates nearly all other strategies on both axes.
- Hamming strategies find primes with much larger arithmetic distance.

This is expected. Standard search explicitly minimizes arithmetic distance.
Hamming search ignores arithmetic distance entirely — it searches in a completely
different direction.

This confirms: **standard search optimizes number-line locality. Hamming search
optimizes bit-space locality. They are not competitors; they solve different problems.**

---

## Multi-objective score

To handle both metrics simultaneously, we define a composite score (lower is better):

$$\text{score} = \text{avg\_checks} + \lambda_H \cdot d_H(x, p) + \lambda_A \cdot \log_2(1 + |p - x|)$$

The log-compression on arithmetic distance prevents it from dominating at large $m$
where arithmetic distances grow exponentially.

Default weights: $\lambda_H = 1.0$, $\lambda_A = 0.25$.

Under this score:
- For low $\lambda_H$ (you barely care about Hamming): standard wins.
- For high $\lambda_H$ (Hamming locality matters): low-bit-first or learned wins.
- The **hybrid policy** — which interleaves standard and Hamming candidates —
  can win across a range of weights.

The results are weight-sensitive, which is another way of saying: the right
strategy depends on what you actually want.

---

## Interpreting the geometry

There is a clean way to think about what these two strategies are doing.

**Standard odd-increment search** walks along the 1-dimensional number line.
Adjacent candidates differ by 2 on the number line. They can differ by many bits.
The search is locally compact on $\mathbb{Z}$.

**Odd-subcube Hamming search** walks in the $(m-1)$-dimensional hypercube.
Adjacent candidates differ by 1 bit. They can differ by a large arithmetic distance.
The search is locally compact on $Q_m^{\text{odd}}$.

These are genuinely different metric spaces. The primes are a fixed set of points,
and their structure looks different in each metric.

The central finding of this project:

> **Prime number search has at least two natural geometries: arithmetic distance
> and Hamming distance. Standard search optimizes number-line locality. Hypercube
> search optimizes bit-space locality. These are different geometries, and neither
> is strictly better.**

---

## What comes next

This project is early-stage. Several directions remain open:

**Larger dimensions** — experiments at $m = 40, 48, 64$ would test whether the
win rates and Pareto structure hold at scale.

**Multiple seeds** — results so far use a single random seed. Confidence intervals
require multiple seeds.

**Weight sensitivity** — systematic sweeps over $\lambda_H$ and $\lambda_A$ would
map the Pareto surface more precisely.

**Smarter hybrid policies** — the current hybrid alternates naively between
standard and Hamming candidates. A learned interleaving might do better.

**Hypercube sieve** — can the modular structure of the hypercube be used to
prescreen candidates, analogous to a sieve of Eratosthenes in bit space?

**Hamming-1 prime pairs** — how many pairs of primes differ by exactly one bit?
What is their structure?

**Modular-residue-aware scoring** — explicitly score bits by their effect on
small modular residues (mod 3, mod 5, mod 7), rather than learning from data.

---

## Closing

We started with a simple question: are primes sparse in Hamming geometry?

The answer: no, they are surprisingly dense. Almost every integer is within 2 bit
flips of a prime.

That observation opened a richer question: can you find primes by searching in
bit space rather than on the number line?

The answer: yes, and when you do, you find a different prime — one that is closer
in bits but further in arithmetic distance. Standard search and Hamming search
are not in competition. They expose different geometric structure in the same set
of primes.

That is the result.

---

*Code: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
