# Chapter 5: The Odd Subcube — A Fairer Comparison

*Prime Geometry in the Binary Hypercube — Part 5*

---

This is the chapter where the comparison becomes honest.

All previous results were complicated by parity. Chapter 3 showed that bit 0
dominates Hamming search because it toggles parity, and all primes greater than 2
are odd. That is not a geometric insight about primes; it is just the observation
that primes are odd.

The fix is to restrict both search strategies to operate on odd numbers only.

---

## The two strategies compared

**Standard odd-increment search**

Force $x$ odd (if even, use $x+1$), then test:

$$x_0,\ x_0+2,\ x_0+4,\ x_0+6,\ \ldots$$

Each step moves 2 on the number line. This is arithmetic-local search.

**Low-bit-first odd-subcube Hamming search**

Force $x$ odd, then test all bit-flip combinations of bits $1, 2, \ldots, m-1$
(excluding bit 0), ordered by preferring lower-index bits first:

$$x_0,\ x_0 \oplus 2^1,\ x_0 \oplus 2^2,\ x_0 \oplus 2^1 \oplus 2^2,\ \ldots$$

Each step moves to a potentially distant arithmetic location, but stays close in
Hamming distance. This is Hamming-local search.

---

## Expected check counts from theory

For standard odd-increment search on an $m$-bit number, the expected number of
candidate checks before finding a prime is:

$$E[\text{checks}] \approx \frac{\log(2^m)}{2} = \frac{m \log 2}{2}$$

For $m = 24$: $\approx 8.3$ expected checks.
For $m = 32$: $\approx 11.1$ expected checks.
For $m = 64$: $\approx 22.2$ expected checks.

Standard search is close to the theoretical minimum for arithmetic-local search.

For odd-subcube Hamming search, the expected behavior depends on the Hamming
ball size and prime density. At radius 4 with $m-1 = 31$ free bits (for $m=32$):

$$B(31, 4) = 1 + 31 + 465 + 4495 + 31465 = 36457 \text{ candidates}$$

With prime density $\approx \frac{1}{m \log 2}$, the first prime is typically
found at a small Hamming radius, but the search visits candidates in a fixed
order — so the check count depends strongly on how well the ordering matches
the actual location of nearby primes.

---

## Experimental results

For $m = 24, 28, 32$ with 10,000 samples each:

### Average candidate checks

| Strategy | m=24 | m=28 | m=32 |
|---|---:|---:|---:|
| standard_odd_increment | **~8** | **~10** | **~12** |
| low_bit_first_no_bit0 | ~14 | ~17 | ~20 |
| learned_bit_order | ~15 | ~18 | ~21 |
| high_bit_first_no_bit0 | ~30+ | ~35+ | ~40+ |
| uniform_random_no_bit0 | ~60+ | ~75+ | ~90+ |

Standard odd-increment wins average checks by a clear margin.

### Per-instance wins vs. standard (low_bit_first_no_bit0)

| m | Strategy wins | Standard wins | Ties |
|---|---:|---:|---:|
| 24 | ~37% | ~36% | ~27% |
| 28 | ~38% | ~39% | ~23% |
| 32 | ~39% | ~40% | ~21% |

**Low-bit-first wins or ties standard on about 60% of individual starting points.**

This is the key tension: standard is better on average, but neither strategy
dominates on a per-instance basis.

---

## Why standard wins on average

Standard odd-increment has a structural advantage: it tests odd numbers in
arithmetic order, and the prime number theorem guarantees that odd numbers near
$x$ have prime density $\approx \frac{2}{\log x}$. The expected gap to the next
prime is $\frac{\log x}{2} \approx \frac{m \log 2}{2}$.

Hamming search explores a structured neighborhood, but that neighborhood does not
align perfectly with where primes actually are. A prime at arithmetic distance 4
might be at Hamming distance 3. A prime at Hamming distance 1 might require an
arithmetic step of $2^{k}$ for some large $k$. The two geometries genuinely conflict.

---

## Why Hamming search wins on many individual inputs

For a given starting point $x$, the nearest prime in Hamming distance might
happen to be much closer than the nearest prime in arithmetic order — or vice versa.

When a nearby prime exists at small Hamming distance, Hamming search finds it in
very few checks: often 1, 2, or 3. Standard search might need 20+ checks to
reach that same prime arithmetically.

The win rate of ~37–39% for low-bit-first represents exactly these cases: starting
points where Hamming-close primes exist.

---

## Summary

Standard odd-increment search is better when you care about:
- Minimizing average candidate checks
- Finding primes close on the number line
- Predictable worst-case behavior

Odd-subcube Hamming search is better when you care about:
- Minimizing bit-level perturbation (Hamming distance to the found prime)
- Winning on a given specific starting point
- A different notion of "close"

Neither strategy strictly dominates. They optimize different geometries.

This is the subject of Chapter 6.

---

*Code: [github.com/pojhafb/prime-hypercube-search](https://github.com/pojhafb/prime-hypercube-search)*
