"""
training/generate_dataset.py
──────────────────────────────────────────────────────────────────────────────
Mathematical Sequence Prediction System — Synthetic Dataset Generator

Generates labelled CSV training data for 16 distinct sequence categories:
    - Arithmetic, Geometric, Prime, Even, Odd, Square, Cube,
      Triangular, Factorial, Powers of 2, Powers of 3, Polynomial,
      Alternating, Increasing, Decreasing, and Custom Pattern.

Each row contains 8 consecutive terms (t_1 … t_8) and a pattern_type label.
All datasets are saved as individual CSV files inside the dataset/ directory.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import csv
import math
import random
import argparse
import logging
from pathlib import Path

# Paths
_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent
_DATASET_DIR = _PROJECT_ROOT / "dataset"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_dataset")

TERMS_PER_ROW = 8
HEADER = [f"t_{i}" for i in range(1, TERMS_PER_ROW + 1)] + ["pattern_type"]
DEFAULT_SAMPLES = 400


# Prime sieve helper
def _sieve(limit: int) -> list[int]:
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = bytearray(len(is_p[i*i::i]))
    return [i for i, v in enumerate(is_p) if v]


PRIMES = _sieve(15_000)
FACTORIALS = [math.factorial(k) for k in range(21)]


# ── Generators ──

def gen_arithmetic(rng: random.Random) -> list[float]:
    a = rng.randint(-50, 150)
    d = rng.choice(list(range(-15, 0)) + list(range(1, 30)))
    return [float(a + i * d) for i in range(TERMS_PER_ROW)]


def gen_geometric(rng: random.Random) -> list[float]:
    a = rng.randint(1, 10)
    r = rng.choice([2, 3, 0.5, 0.25, -2, -3])
    seq = [float(a * (r ** i)) for i in range(TERMS_PER_ROW)]
    if any(abs(v) > 1e10 for v in seq):
        a = rng.randint(1, 3)
        r = rng.choice([2, 0.5])
        seq = [float(a * (r ** i)) for i in range(TERMS_PER_ROW)]
    return seq


def gen_prime(rng: random.Random) -> list[float]:
    max_start = len(PRIMES) - TERMS_PER_ROW - 1
    start_idx = rng.randint(0, max_start)
    return [float(PRIMES[start_idx + i]) for i in range(TERMS_PER_ROW)]


def gen_even(rng: random.Random) -> list[float]:
    a = rng.choice(range(-50, 150, 2))
    d = rng.choice(range(2, 20, 2)) if rng.choice([True, False]) else rng.choice(range(-20, 0, 2))
    return [float(a + i * d) for i in range(TERMS_PER_ROW)]


def gen_odd(rng: random.Random) -> list[float]:
    a = rng.choice(range(-49, 151, 2))
    d = rng.choice(range(2, 20, 2)) if rng.choice([True, False]) else rng.choice(range(-20, 0, 2))
    return [float(a + i * d) for i in range(TERMS_PER_ROW)]


def gen_square(rng: random.Random) -> list[float]:
    start = rng.randint(1, 40)
    return [float((start + i) ** 2) for i in range(TERMS_PER_ROW)]


def gen_cube(rng: random.Random) -> list[float]:
    start = rng.randint(1, 20)
    return [float((start + i) ** 3) for i in range(TERMS_PER_ROW)]


def gen_triangular(rng: random.Random) -> list[float]:
    start = rng.randint(1, 50)
    return [float((start + i) * (start + i + 1) // 2) for i in range(TERMS_PER_ROW)]


def gen_factorial(rng: random.Random) -> list[float]:
    max_start = len(FACTORIALS) - TERMS_PER_ROW - 1
    start = rng.randint(0, max_start)
    return [float(FACTORIALS[start + i]) for i in range(TERMS_PER_ROW)]


def gen_powers_of_2(rng: random.Random) -> list[float]:
    start = rng.randint(0, 12)
    return [float(2 ** (start + i)) for i in range(TERMS_PER_ROW)]


def gen_powers_of_3(rng: random.Random) -> list[float]:
    start = rng.randint(0, 8)
    return [float(3 ** (start + i)) for i in range(TERMS_PER_ROW)]


def gen_polynomial(rng: random.Random) -> list[float]:
    # Randomly quadratic or cubic
    if rng.choice([True, False]):
        a = rng.randint(1, 4)
        b = rng.randint(-5, 5)
        c = rng.randint(0, 15)
        start = rng.randint(0, 10)
        return [float(a * (start + i)**2 + b * (start + i) + c) for i in range(TERMS_PER_ROW)]
    else:
        a = rng.randint(1, 2)
        b = rng.randint(-3, 3)
        c = rng.randint(0, 5)
        d = rng.randint(0, 10)
        start = rng.randint(0, 5)
        return [float(a * (start + i)**3 + b * (start + i)**2 + c * (start + i) + d) for i in range(TERMS_PER_ROW)]


def gen_alternating(rng: random.Random) -> list[float]:
    choice = rng.randint(0, 2)
    if choice == 0:
        val = rng.randint(1, 50)
        return [float(val * ((-1) ** i)) for i in range(TERMS_PER_ROW)]
    elif choice == 1:
        a = float(rng.randint(1, 10))
        r = rng.choice([-2, -3, -0.5])
        return [a * (r ** i) for i in range(TERMS_PER_ROW)]
    else:
        a = float(rng.randint(1, 20))
        d = float(rng.randint(1, 5))
        return [(a + i * d) * ((-1) ** i) for i in range(TERMS_PER_ROW)]


def gen_increasing(rng: random.Random) -> list[float]:
    seq = [float(rng.randint(-50, 50))]
    for _ in range(TERMS_PER_ROW - 1):
        step = rng.uniform(0.5, 10.0)
        seq.append(seq[-1] + step)
    return seq


def gen_decreasing(rng: random.Random) -> list[float]:
    seq = [float(rng.randint(-50, 50))]
    for _ in range(TERMS_PER_ROW - 1):
        step = rng.uniform(0.5, 10.0)
        seq.append(seq[-1] - step)
    return seq


def gen_custom(rng: random.Random) -> list[float]:
    choice = rng.randint(0, 2)
    if choice == 0:
        # Generalised Fibonacci: Lucas sequence seeds (2, 1)
        t1, t2 = 2.0, 1.0
        seq = [t1, t2]
        for _ in range(TERMS_PER_ROW - 2):
            seq.append(seq[-1] + seq[-2])
        return seq
    elif choice == 1:
        # Alternating add and multiply
        a = float(rng.randint(1, 10))
        d = float(rng.randint(1, 5))
        r = float(rng.randint(2, 3))
        seq = [a]
        for i in range(1, TERMS_PER_ROW):
            seq.append(seq[-1] + d if i % 2 == 1 else seq[-1] * r)
        return seq
    else:
        # Sum of first n squares
        start = rng.randint(0, 8)
        seq = []
        for i in range(TERMS_PER_ROW):
            n = start + i + 1
            seq.append(float(n * (n + 1) * (2*n + 1) // 6))
        return seq


def _is_valid(seq: list[float]) -> bool:
    for v in seq:
        if not math.isfinite(v) or abs(v) > 1e12:
            return False
    return True


# ── Writer ──

def write_dataset_csv(path: Path, rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)
    logger.info("  Generated: %-32s (%d rows)", path.name, len(rows))


# ── Pipeline orchestrator ──

def generate_all_datasets(output_dir: Path, n_samples: int, seed: int) -> dict:
    rng = random.Random(seed)

    categories = {
        "arithmetic.csv": (gen_arithmetic, "arithmetic"),
        "geometric.csv": (gen_geometric, "geometric"),
        "prime.csv": (gen_prime, "prime"),
        "even.csv": (gen_even, "even"),
        "odd.csv": (gen_odd, "odd"),
        "square.csv": (gen_square, "square"),
        "cube.csv": (gen_cube, "cube"),
        "triangular.csv": (gen_triangular, "triangular"),
        "factorial.csv": (gen_factorial, "factorial"),
        "powers_of_2.csv": (gen_powers_of_2, "powers_of_2"),
        "powers_of_3.csv": (gen_powers_of_3, "powers_of_3"),
        "polynomial.csv": (gen_polynomial, "polynomial"),
        "alternating.csv": (gen_alternating, "alternating"),
        "increasing.csv": (gen_increasing, "increasing"),
        "decreasing.csv": (gen_decreasing, "decreasing"),
        "custom_dataset.csv": (gen_custom, "custom"),
    }

    stats = {}
    for filename, (gen_fn, label) in categories.items():
        rows = []
        while len(rows) < n_samples:
            try:
                seq = gen_fn(rng)
                if _is_valid(seq):
                    rows.append([round(v, 6) for v in seq] + [label])
            except Exception:
                pass
        write_dataset_csv(output_dir / filename, rows)
        stats[filename] = len(rows)

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic mathematical sequence dataset generator.")
    parser.add_argument("--output", type=Path, default=_DATASET_DIR, help="Directory to save CSVs.")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES, help="Samples per CSV file.")
    parser.add_argument("--seed", type=int, default=42, help="Random number generator seed.")
    args = parser.parse_args()

    print()
    print("+------------------------------------------------------+")
    print("|   SeqPredict — Sequence Dataset Generator            |")
    print("+------------------------------------------------------+")
    print(f"  Destination directory : {args.output}")
    print(f"  Samples per category  : {args.samples}")
    print(f"  Random seed           : {args.seed}")
    print()

    try:
        stats = generate_all_datasets(args.output, args.samples, args.seed)
        total = sum(stats.values())
        print()
        print("  TOTAL synthetic rows generated:", total)
        print("  All datasets saved successfully.")
        return 0
    except Exception as exc:
        logger.error("Dataset generation aborted with error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())