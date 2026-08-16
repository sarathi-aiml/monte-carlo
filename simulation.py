"""Monte Carlo model for a bake sale."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import fmean, median


@dataclass(frozen=True)
class Assumptions:
    min_attendance: int = 80
    max_attendance: int = 180
    min_purchase_rate: float = 0.30
    max_purchase_rate: float = 0.70
    min_purchase_amount: float = 3.00
    max_purchase_amount: float = 8.00
    fixed_cost: float = 250.00

    def validate(self) -> None:
        if self.min_attendance < 0 or self.min_attendance > self.max_attendance:
            raise ValueError("attendance bounds must be non-negative and ordered")
        if not 0 <= self.min_purchase_rate <= self.max_purchase_rate <= 1:
            raise ValueError("purchase-rate bounds must be between 0 and 1")
        if self.min_purchase_amount < 0 or self.min_purchase_amount > self.max_purchase_amount:
            raise ValueError("purchase-amount bounds must be non-negative and ordered")
        if self.fixed_cost < 0:
            raise ValueError("fixed cost cannot be negative")


@dataclass(frozen=True)
class Outcome:
    attendance: int
    purchase_rate: float
    customers: int
    purchase_amount: float
    revenue: float
    profit: float


def simulate(trials: int = 10_000, seed: int = 42, assumptions: Assumptions | None = None) -> list[Outcome]:
    """Return independently simulated bake-sale outcomes."""
    if trials <= 0:
        raise ValueError("trials must be greater than zero")
    assumptions = assumptions or Assumptions()
    assumptions.validate()
    rng = Random(seed)
    outcomes: list[Outcome] = []

    for _ in range(trials):
        attendance = rng.randint(assumptions.min_attendance, assumptions.max_attendance)
        purchase_rate = rng.uniform(assumptions.min_purchase_rate, assumptions.max_purchase_rate)
        purchase_amount = rng.uniform(assumptions.min_purchase_amount, assumptions.max_purchase_amount)
        # Each attendee makes an independent purchase decision.
        customers = sum(rng.random() < purchase_rate for _ in range(attendance))
        revenue = customers * purchase_amount
        outcomes.append(
            Outcome(
                attendance=attendance,
                purchase_rate=purchase_rate,
                customers=customers,
                purchase_amount=purchase_amount,
                revenue=revenue,
                profit=revenue - assumptions.fixed_cost,
            )
        )
    return outcomes


def percentile(values: list[float], probability: float) -> float:
    """Calculate a linearly interpolated percentile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize(outcomes: list[Outcome]) -> dict[str, float]:
    if not outcomes:
        raise ValueError("at least one outcome is required")
    profits = [outcome.profit for outcome in outcomes]
    return {
        "trials": float(len(outcomes)),
        "profit_probability": sum(value > 0 for value in profits) / len(profits),
        "average_profit": fmean(profits),
        "median_profit": median(profits),
        "p05_profit": percentile(profits, 0.05),
        "p95_profit": percentile(profits, 0.95),
        "worst_profit": min(profits),
        "best_profit": max(profits),
    }
