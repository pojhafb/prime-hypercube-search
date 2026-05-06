# Chapter 1: Primes in the Binary Hypercube

*Prime Geometry in the Binary Hypercube — Part 1*

---

We all learn about prime numbers on the number line. A prime sits at a point,
and we measure how far it is from another number by simple subtraction:

$$|p - x|$$

This is arithmetic distance — the geometry of the number line.

But integers have another representation: binary strings. Every integer can be
written as a sequence of bits. And once you have binary strings, you have a
natural geometry that has nothing to do with subtraction.

This series is about what happens when you take that geometry seriously.

---

## The binary hypercube

For any positive integer $m$, the $m$-bit binary hypercube is the set of all
$m$-bit strings:

$$Q_m = \{0,1\}^m$$

Each element is a vertex. Two vertices are adjacent if they differ in exactly
one bit — a single bit flip. The number of bit positions where two strings
differ is called the **Hamming distance**:

$$d_H(x, y) = \text{(number of bit positions where } x \text{ and } y \text{ differ)}$$

For 1-bit strings, the hypercube is just two nodes: 0 and 1.
For 2-bit strings, it is a square: 00, 01, 10, 11.
For 3-bit strings, it is a cube: the familiar 3D cube with vertices labeled in binary.
For $m$ bits, it is a hypercube with $2^m$ vertices.

Every integer from 0 to $2^m - 1$ corresponds to exactly one vertex.

---

## Primes as vertices

Within $Q_m$, the prime numbers form a subset of vertices:

$$P_m = \{x \in Q_m : x \text{ is prime}\}$$

The prime number theorem tells us that among integers near $N$, roughly
$\frac{1}{\log N}$ of them are prime. For an $m$-bit integer, $\log N \approx m \log 2$,
so the prime density is roughly $\frac{1}{m \log 2}$.

Primes are sparse on the number line. They thin out as numbers grow.

The question that started this project:

> **Are primes also sparse in Hamming geometry?**

The answer turns out to be: much less so.

---

## Hamming balls grow fast

On the number line, the "ball" of radius $r$ around $x$ contains $2r$ integers.
It grows linearly.

In the hypercube, the ball of radius $r$ around $x$ — meaning all vertices within
$r$ bit flips — has size:

$$B(m, r) = \sum_{i=0}^{r} \binom{m}{i}$$

For $m = 32$ and $r = 4$:

$$B(32, 4) = 1 + 32 + 496 + 4960 + 35960 = 41449$$

That is over 41,000 candidate integers within just 4 bit flips of any starting point.

Even if only $\frac{1}{m \log 2} \approx \frac{1}{22}$ of them are prime, the expected
number of primes within Hamming radius 4 of a random 32-bit number is roughly:

$$41449 \times \frac{1}{22} \approx 1884 \text{ primes}$$

The Hamming neighborhood is so large that it almost certainly contains a prime nearby.

---

## The central question

This suggests reframing prime search entirely:

> Instead of walking the number line looking for the next prime,
> what if we searched by bit flips?

That is what this series investigates. We compare two search geometries:

**Number-line search** — test $x$, $x+2$, $x+4$, $\ldots$ until a prime is found.

**Hamming search** — try all vertices within Hamming radius 1 of $x$, then radius 2,
radius 3, $\ldots$, until a prime is found.

In both cases we are looking for "a prime near $x$," but "near" means something
completely different.

The rest of this series documents what we found.

---

## What comes next

- **Chapter 2**: We measure the actual Hamming distance from every integer to its
  nearest prime. The result is surprisingly small.
- **Chapter 3**: We find that not all bit directions are equally useful for reaching primes.
- **Chapter 4**: We learn a search policy from data and test whether it transfers to
  larger dimensions.
- **Chapter 5**: We restrict to the odd subcube — a fairer comparison with standard search.
- **Chapter 6**: We frame the result as a Pareto problem: two geometries, neither
  strictly better.

---

*Code for all experiments: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
