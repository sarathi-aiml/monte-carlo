import unittest

from simulation import Assumptions, simulate, summarize


class SimulationTests(unittest.TestCase):
    def test_seed_is_reproducible(self):
        self.assertEqual(simulate(10, seed=42), simulate(10, seed=42))

    def test_outcomes_stay_within_assumptions(self):
        assumptions = Assumptions()
        for result in simulate(100, assumptions=assumptions):
            self.assertLessEqual(result.customers, result.attendance)
            self.assertAlmostEqual(result.profit, result.revenue - assumptions.fixed_cost)
            self.assertGreaterEqual(result.purchase_rate, assumptions.min_purchase_rate)
            self.assertLessEqual(result.purchase_rate, assumptions.max_purchase_rate)

    def test_summary_probability_is_valid(self):
        stats = summarize(simulate(100))
        self.assertGreaterEqual(stats["profit_probability"], 0)
        self.assertLessEqual(stats["profit_probability"], 1)

    def test_invalid_trial_count(self):
        with self.assertRaises(ValueError):
            simulate(0)


if __name__ == "__main__":
    unittest.main()
