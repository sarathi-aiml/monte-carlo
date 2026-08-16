#!/usr/bin/env python3
"""Run the bake-sale Monte Carlo simulation and create a histogram."""

from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path

from simulation import Outcome, simulate, summarize


def money(value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"


def write_csv(outcomes: list[Outcome], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("attendance", "purchase_rate", "customers", "purchase_amount", "revenue", "profit"))
        for row in outcomes:
            writer.writerow((row.attendance, f"{row.purchase_rate:.6f}", row.customers,
                             f"{row.purchase_amount:.2f}", f"{row.revenue:.2f}", f"{row.profit:.2f}"))


def write_histogram(outcomes: list[Outcome], average: float, path: Path, bins: int = 40) -> None:
    """Write a dependency-free SVG histogram."""
    values = [row.profit for row in outcomes]
    low, high = min(values), max(values)
    span = high - low or 1
    counts = [0] * bins
    for value in values:
        index = min(int((value - low) / span * bins), bins - 1)
        counts[index] += 1

    width, height = 1000, 600
    left, right, top, bottom = 90, 35, 55, 85
    plot_w, plot_h = width - left - right, height - top - bottom
    max_count = max(counts) or 1
    bar_w = plot_w / bins
    bars = []
    for index, count in enumerate(counts):
        bar_h = count / max_count * plot_h
        bars.append(f'<rect x="{left + index * bar_w:.2f}" y="{top + plot_h - bar_h:.2f}" '
                    f'width="{max(bar_w - 1, 1):.2f}" height="{bar_h:.2f}" fill="#4f86c6"/>')

    def x(value: float) -> float:
        return left + (value - low) / span * plot_w

    markers = []
    if low <= 0 <= high:
        markers.append(f'<line x1="{x(0):.2f}" x2="{x(0):.2f}" y1="{top}" y2="{top + plot_h}" stroke="#d43f3a" stroke-width="3" stroke-dasharray="9 7"/>')
        markers.append(f'<text x="{x(0) + 7:.2f}" y="{top + 20}" fill="#a52a2a">Break-even</text>')
    markers.append(f'<line x1="{x(average):.2f}" x2="{x(average):.2f}" y1="{top}" y2="{top + plot_h}" stroke="#173f73" stroke-width="3" stroke-dasharray="9 7"/>')
    markers.append(f'<text x="{x(average) + 7:.2f}" y="{top + 42}" fill="#173f73">Average {escape(money(average))}</text>')
    ticks = []
    for index in range(6):
        value = low + span * index / 5
        tx = x(value)
        ticks.append(f'<line x1="{tx:.2f}" x2="{tx:.2f}" y1="{top + plot_h}" y2="{top + plot_h + 7}" stroke="#333"/>')
        ticks.append(f'<text x="{tx:.2f}" y="{top + plot_h + 28}" text-anchor="middle">{escape(money(value))}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" font-size="14" fill="#222">
<text x="{width / 2}" y="30" text-anchor="middle" font-size="22" font-weight="bold">Simulated Bake Sale Profit and Loss</text>
<line x1="{left}" x2="{left}" y1="{top}" y2="{top + plot_h}" stroke="#333"/>
<line x1="{left}" x2="{left + plot_w}" y1="{top + plot_h}" y2="{top + plot_h}" stroke="#333"/>
{''.join(bars)}{''.join(markers)}{''.join(ticks)}
<text x="{width / 2}" y="{height - 20}" text-anchor="middle" font-size="16">Profit / loss per event</text>
<text x="22" y="{height / 2}" transform="rotate(-90 22 {height / 2})" text-anchor="middle" font-size="16">Number of simulations</text>
</g></svg>'''
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate the profitability of a bake sale.")
    parser.add_argument("--trials", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    outcomes = simulate(args.trials, args.seed)
    stats = summarize(outcomes)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(outcomes, args.output_dir / "simulation_results.csv")
    write_histogram(outcomes, stats["average_profit"], args.output_dir / "profit_histogram.svg")

    print(f"Trials:                 {int(stats['trials']):,}")
    print(f"Chance of profit:       {stats['profit_probability']:.1%}")
    print(f"Average profit:         {money(stats['average_profit'])}")
    print(f"Median profit:          {money(stats['median_profit'])}")
    print(f"90% outcome range:      {money(stats['p05_profit'])} to {money(stats['p95_profit'])}")
    print(f"Worst / best outcome:   {money(stats['worst_profit'])} / {money(stats['best_profit'])}")
    print(f"\nSaved results to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
