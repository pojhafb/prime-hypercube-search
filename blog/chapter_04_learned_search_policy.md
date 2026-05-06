# Chapter 4: Learning a Bit-Flip Search Policy

*Prime Geometry in the Binary Hypercube — Part 4*

---

Chapter 3 established that in the odd subcube, low-order bits are modestly more
useful than high-order bits for reaching primes. The question now: can we learn
a better ordering from data, and does it transfer to larger dimensions?

---

## The idea

Instead of sorting bit positions by a fixed rule (lowest first, highest first,
random), we ask: which bits have historically appeared most often in successful
prime-finding paths?

We run a training experiment on dimension $m_{\text{train}}$:

1. Sample many random odd $m$-bit starting points.
2. For each, run the teacher policy (low-bit-first) and record which bit positions
   appear in the flip set that reached a prime.
3. Count occurrences per bit position: bit $b$ gets score $\text{score}[b] = \text{count}[b]$.
4. Use these scores to rank bits: higher score → try this bit earlier.

The resulting **learned bit-order policy** replaces the fixed sorting key with a
data-driven one.

---

## The flip-set ordering

For a set of positions $\{b_1, b_2, \ldots, b_r\}$ (a flip set of radius $r$),
the learned policy sorts by:

$$\text{key}(c) = \left(-\sum_{b \in c} \text{score}[b],\ \sum_{b \in c} b,\ \max(c)\right)$$

Higher total score → earlier. Ties broken by preferring lower-index bits.

This means the policy tries high-scoring bit combinations first.

---

## Transfer across dimensions

The interesting scientific question is whether a policy learned at $m_{\text{train}}$
remains useful at $m_{\text{test}} > m_{\text{train}}$.

Transfer works as follows:

- Bits $0 \ldots m_{\text{train}}-1$: keep their learned scores.
- New bits $m_{\text{train}} \ldots m_{\text{test}}-1$: assign a small fallback score
  (25% of the minimum positive score).

The intuition: if bit 3 was useful at $m=20$, it should still be useful at $m=32$,
because the local modular structure (mod 8, mod small primes) is the same.

High-order bits that did not exist during training get low priority — they are
tried last.

---

## Results (before the odd subcube correction)

When we tested transfer in the full hypercube ($m_{\text{train}} = 16$, $m_{\text{test}} = 18, 20$),
the learned policy consistently outperformed uniform random search and also improved
slightly over pure low-bit-first.

The learned policy successfully rediscovered:
- Bit 0 as the top-ranked bit (parity advantage)
- Low-order bits as the next tier
- Monotonically decreasing scores for higher bits

This validated the transfer mechanism, but the result was dominated by the parity
signal discussed in Chapter 3.

---

## Results after the odd subcube correction

After restricting to the odd subcube (bit 0 excluded), the learned policy became
almost identical to low-bit-first.

This was the honest finding:

> **Most of what the learned policy was learning was the parity advantage of bit 0.
> Once parity is controlled, the learned policy adds only a small benefit over
> low-bit-first.**

The learned policy still transfers across dimensions and still beats uniform random
search in the odd subcube. But the gap over low-bit-first is small.

---

## What this means

The transfer experiment is still scientifically meaningful for two reasons:

1. It confirms that bit-direction usefulness is a real, learnable, transferable signal.
2. It shows that the dominant source of that signal is parity, not deeper prime geometry.

This sets up the right framing for Chapter 5: now that we have removed the parity
confound, how does the best Hamming strategy (low-bit-first) actually compare to
standard odd-increment search?

---

## Code

The trainer lives in `src/primecube/training/trainer.py`.
Transfer logic is in `src/primecube/training/transfer.py`.

To run:
```bash
python scripts/run_odd_subcube_pareto.py
```

The runner trains on `train_m`, transfers scores to each `test_m`, and
evaluates all strategies including the learned policy.

---

*Code: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
