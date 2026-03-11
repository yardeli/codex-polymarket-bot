import unittest

from bot.models import MarketDirection, WeatherMarket, WeatherMetric
from bot.noaa import ForecastSlices, probability_for_market


class ProbabilityTests(unittest.TestCase):
    def test_above_probability(self) -> None:
        market = WeatherMarket("1", "Miami", 0, 0, WeatherMetric.HUMIDITY, MarketDirection.ABOVE, 75, None, 0.1, 10)
        slices = ForecastSlices([70, 80, 90], [], [])
        self.assertEqual(round(probability_for_market(market, slices), 2), 0.67)

    def test_between_probability(self) -> None:
        market = WeatherMarket("2", "Denver", 0, 0, WeatherMetric.TEMPERATURE, MarketDirection.BETWEEN, 0, 5, 0.13, 13)
        slices = ForecastSlices([], [1, 3, 8], [])
        self.assertEqual(round(probability_for_market(market, slices), 2), 0.67)


if __name__ == "__main__":
    unittest.main()
