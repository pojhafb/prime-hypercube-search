from __future__ import annotations

from collections import Counter

import pandas as pd

from .prime_indicator import PrimeIndicator


class _UnionFind:
    """Path-compressed union-find over arbitrary hashable elements."""

    def __init__(self, elements: list) -> None:
        self._parent: dict = {e: e for e in elements}
        self._rank: dict = {e: 0 for e in elements}

    def find(self, x: int) -> int:
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1


class PrimeInducedGraph:
    """
    G_m^prime: vertices = P_m ∩ Q_m^odd, edges = Hamming-1 prime pairs.

    Analyzes connectivity via union-find in O(|P_m| * m) time.
    """

    def __init__(self, m: int) -> None:
        self.m = m

    def analyze(self, prime_set: set[int] | None = None) -> dict:
        """Full connectivity + degree analysis.  Returns a summary dict."""
        pi = PrimeIndicator(self.m, odd_only=True)
        if prime_set is None:
            prime_set = pi.prime_set()

        primes = sorted(prime_set)
        n = len(primes)
        uf = _UnionFind(primes)
        degree: dict[int, int] = {p: 0 for p in primes}
        edge_count = 0

        free_bits = list(range(1, self.m))
        for p in primes:
            for j in free_bits:
                neighbor = p ^ (1 << j)
                if neighbor in prime_set and neighbor > p:
                    uf.union(p, neighbor)
                    degree[p] += 1
                    degree[neighbor] += 1
                    edge_count += 1

        # Collect components
        comp_map: dict[int, list[int]] = {}
        for p in primes:
            root = uf.find(p)
            comp_map.setdefault(root, []).append(p)

        sizes = sorted((len(v) for v in comp_map.values()), reverse=True)
        size_dist = Counter(sizes)

        return {
            "m": self.m,
            "n_primes": n,
            "n_edges": edge_count,
            "n_components": len(comp_map),
            "largest_component": sizes[0] if sizes else 0,
            "largest_fraction": sizes[0] / n if n else 0.0,
            "second_largest": sizes[1] if len(sizes) > 1 else 0,
            "isolated_count": size_dist.get(1, 0),
            "isolated_fraction": size_dist.get(1, 0) / n if n else 0.0,
            "avg_degree": 2 * edge_count / n if n else 0.0,
            "max_degree": max(degree.values()) if degree else 0,
            "component_sizes": sizes,
            "size_distribution": dict(size_dist),
            "degree_distribution": dict(Counter(degree.values())),
        }

    def component_size_df(self, result: dict) -> pd.DataFrame:
        """DataFrame of component size → count."""
        dist = result["size_distribution"]
        rows = [
            {
                "component_size": k,
                "n_components": v,
                "n_primes_in_class": k * v,
                "fraction_of_primes": k * v / result["n_primes"],
            }
            for k, v in sorted(dist.items())
        ]
        return pd.DataFrame(rows)

    def degree_df(self, result: dict) -> pd.DataFrame:
        """DataFrame of degree → count."""
        dist = result["degree_distribution"]
        return pd.DataFrame(
            [{"degree": k, "n_primes": v} for k, v in sorted(dist.items())]
        )

    def compare_to_random(
        self,
        prime_set: set[int],
        n_seeds: int = 10,
        seed: int = 42,
    ) -> pd.DataFrame:
        """Run the same analysis on random same-density subsets and return comparison."""
        import random

        pi = PrimeIndicator(self.m, odd_only=True)
        vertices = pi.vertices()
        density = len(prime_set) / len(vertices)

        real_result = self.analyze(prime_set)

        baseline_rows: list[dict] = []
        for k in range(n_seeds):
            rng = random.Random(seed + k)
            rnd_set = {v for v in vertices if rng.random() < density}
            r = self.analyze(rnd_set)
            baseline_rows.append(
                {
                    "seed": seed + k,
                    "n_primes": r["n_primes"],
                    "n_edges": r["n_edges"],
                    "n_components": r["n_components"],
                    "largest_fraction": r["largest_fraction"],
                    "isolated_fraction": r["isolated_fraction"],
                    "avg_degree": r["avg_degree"],
                }
            )

        bl_df = pd.DataFrame(baseline_rows)
        comparison = {
            "metric": [
                "n_edges", "n_components", "largest_fraction",
                "isolated_fraction", "avg_degree",
            ],
            "prime_value": [
                real_result["n_edges"],
                real_result["n_components"],
                real_result["largest_fraction"],
                real_result["isolated_fraction"],
                real_result["avg_degree"],
            ],
            "baseline_mean": [
                bl_df["n_edges"].mean(),
                bl_df["n_components"].mean(),
                bl_df["largest_fraction"].mean(),
                bl_df["isolated_fraction"].mean(),
                bl_df["avg_degree"].mean(),
            ],
            "baseline_std": [
                bl_df["n_edges"].std(),
                bl_df["n_components"].std(),
                bl_df["largest_fraction"].std(),
                bl_df["isolated_fraction"].std(),
                bl_df["avg_degree"].std(),
            ],
        }
        cdf = pd.DataFrame(comparison)
        cdf["ratio"] = cdf["prime_value"] / cdf["baseline_mean"]
        cdf["sigma"] = (cdf["prime_value"] - cdf["baseline_mean"]) / cdf["baseline_std"]
        return cdf
