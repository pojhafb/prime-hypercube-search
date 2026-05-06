# Chapter 3: The Directional Bias Toward Primes

*Prime Geometry in the Binary Hypercube — Part 3*

---

Chapter 2 showed that most integers are within 2 bit flips of a prime.
The natural next question: which bit positions are doing the work?

We tracked which bits were flipped in every successful prime-finding path and
built a histogram. The answer was striking — and then we looked more carefully.

---

## Bit 0 dominates in the full hypercube

In the full $Q_m$ search (all integers, not just odd ones), the flip-position
distribution shows an enormous spike at bit 0.

This makes sense immediately. Bit 0 controls parity:

- If bit 0 is 0, the integer is even.
- If bit 0 is 1, the integer is odd.
- Every prime greater than 2 is odd.

So roughly half of all integers are even. For an even integer, the single fastest
path to a prime is to flip bit 0. No other single-bit flip can turn an even number
odd — they all change higher-order bits while leaving parity unchanged.

The result is that bit 0 appears in the flip path for nearly half of all starting
points. Every other bit position is used far less often.

This is a real signal, but it is almost entirely a parity signal. It tells us
very little about the structure of primes beyond their oddness.

---

## The problem with parity dominance

If we design a search policy based on this signal — "try bit 0 first" — we get
a strategy that is mostly just doing:

> turn the number odd, then check

That is essentially the first step of standard odd-increment search. It is not
a hypercube insight; it is a parity observation.

To get a genuine geometric result, we need to remove this confound.

---

## The odd subcube

We restrict to the **odd subcube**:

$$Q_m^{\text{odd}} = \{x \in Q_m : \text{bit}_0(x) = 1\}$$

This is the set of all odd $m$-bit integers. It has $2^{m-1}$ elements.

Within this subspace:
- Bit 0 is permanently 1 — it is never flipped.
- All search candidates remain odd.
- We are comparing apples to apples: both Hamming search and number-line search
  operate on odd numbers only.

All flip sets in the codebase are built on `allowed_bits = range(1, m)` — bits 1
through $m-1$. Bit 0 is excluded by construction.

---

## Directional bias in the odd subcube

With parity removed, the flip-position distribution becomes more nuanced.

Low-order bits (bits 1, 2, 3) still appear more often than high-order bits.
This reflects the structure of modular arithmetic:

- Bit 1 controls whether the number is $\equiv 1$ or $3 \pmod{4}$.
- Bits 1 and 2 together determine the residue mod 8.
- Low-order bits affect many small modular constraints simultaneously.

Primes are not uniformly distributed across residue classes — they must avoid
multiples of 2, 3, 5, 7, and so on. Flipping low-order bits changes these
small-modulus residues, which can either help or hurt.

The net effect: low-order bits are modestly more useful than high-order bits
for reaching primes quickly, but the signal is much weaker than the parity spike.

---

## Summary of findings

| Regime | Dominant signal | Explanation |
|--------|----------------|-------------|
| Full hypercube | Bit 0 overwhelmingly | Parity: even numbers need bit 0 flipped to become odd |
| Odd subcube | Low-order bits slightly preferred | Modular structure (mod 4, mod 8, mod small primes) |

The key methodological lesson:

> **Fair comparison requires the odd subcube.**
> The parity advantage of bit 0 is not a geometric insight about primes —
> it is just the observation that primes are odd.

All subsequent experiments operate in the odd subcube.

---

*Code: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
