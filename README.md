# Prime Hypercube Search

This repository explores prime search in binary hypercube geometry.

Instead of viewing integers only on the number line, we represent m-bit integers
as vertices of Q_m = {0,1}^m. Two numbers are adjacent if their binary representations
differ by exactly one bit. We compare ordinary number-line prime search with
Hamming-space search strategies that flip bits while preserving oddness.

## Main questions

1. How close is a typical integer to a prime in Hamming distance?
2. Which bit directions are most useful for reaching primes?
3. Can learned bit-flip policies transfer across dimensions?
4. How does odd-subcube Hamming search compare to standard odd-increment search?
5. What is the Pareto tradeoff between candidate checks, Hamming distance, and arithmetic distance?

## Key early findings

- Standard odd-increment search has the lowest average candidate-check count.
- Odd-subcube Hamming search wins or ties standard search on ~58–60% of individual starting values.
- Hamming strategies find primes with substantially smaller bit-level perturbation.
- Arithmetic and Hamming locality define different search geometries.
- The most honest framing: prime search has at least two natural geometries.

## Terminology

| Concept | Term |
|---|---|
| Full m-bit hypercube | binary hypercube |
| Odd-only subspace (bit 0 = 1) | odd subcube |
| Search by adding 2 | standard odd-increment search |
| Search by bit flips excluding bit 0 | odd-subcube Hamming search |
| Learned bit ranking | learned bit-order policy |
| Combined arithmetic + bit search | hybrid search policy |
| Evaluation across checks/Hamming/arithmetic | Pareto geometry of prime search |

## Repository layout

```
src/primecube/
    core/           bit_ops, prime_tester, models, flip_sets
    policies/       standard_odd, hamming, hybrid, base
    training/       trainer (learns bit scores), transfer (cross-dimension)
    experiments/    runner (policy-agnostic experiment loop)
    analysis/       metrics, wins, pareto
    plotting/       charts (saves PNG, optional show)

scripts/
    run_odd_subcube_pareto.py       main experiment
    run_distance_distribution.py    Chapter 2 distance result

results/
    raw/        per-run CSVs
    summaries/  aggregated statistics
    plots/      PNG charts

tests/
    test_bit_ops.py
    test_flip_sets.py
    test_policies.py
    test_metrics.py

blog/
    chapter_01_primes_in_the_hypercube.md
    ...
```

## Quick start

```bash
cd prime-hypercube-search
pip install -r requirements.txt

# Distance distribution (Chapter 2 result, ~1 min)
python scripts/run_distance_distribution.py

# Full policy comparison (quick run, ~5–15 min depending on hardware)
python scripts/run_odd_subcube_pareto.py

# Larger credibility run
python scripts/run_odd_subcube_pareto.py \
    --train-m 24 \
    --test-ms 32 40 48 \
    --train-samples 20000 \
    --test-samples 50000

# Show plots interactively (in addition to saving)
python scripts/run_odd_subcube_pareto.py --show-plots
```

## Running tests

```bash
pytest tests/
```

## Blog series: Prime Geometry in the Binary Hypercube

| Chapter | File | Topic |
|---|---|---|
| 1 | `blog/chapter_01_primes_in_the_hypercube.md` | Introducing the hypercube model |
| 2 | `blog/chapter_02_distance_to_nearest_prime.md` | Hamming distance distribution |
| 3 | `blog/chapter_03_directional_bias.md` | Which bits lead to primes |
| 4 | `blog/chapter_04_learned_search_policy.md` | Learning and transferring policies |
| 5 | `blog/chapter_05_odd_subcube_vs_standard.md` | Fair comparison in the odd subcube |
| 6 | `blog/chapter_06_pareto_geometry.md` | Two geometries of prime search |
