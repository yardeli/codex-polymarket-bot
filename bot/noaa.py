from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

from bot.models import MarketDirection, WeatherMarket, WeatherMetric


@dataclass(slots=True)
class ForecastSlices:
    humidity_values: list[float]
    temperature_values: list[float]
    rain_probability_values: list[float]


class NoaaClient:
    BASE = "https://api.weather.gov"

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def close(self) -> None:
        return

    def _get_json(self, url: str) -> dict:
        req = Request(url, headers={"User-Agent": "polymarket-weather-bot/1.0"})
        with urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _grid_url_for(self, lat: float, lon: float) -> str:
        payload = self._get_json(f"{self.BASE}/points/{lat},{lon}")
        return payload["properties"]["forecastGridData"]

    def get_slices_48h(self, lat: float, lon: float) -> ForecastSlices:
        grid_url = self._grid_url_for(lat, lon)
        props = self._get_json(grid_url)["properties"]
        cutoff = datetime.now(timezone.utc) + timedelta(hours=48)

        def extract_values(path: str) -> list[float]:
            entries = props.get(path, {}).get("values", [])
            vals: list[float] = []
            for e in entries:
                t = datetime.fromisoformat(e["validTime"].split("/")[0].replace("Z", "+00:00"))
                if t <= cutoff and e.get("value") is not None:
                    vals.append(float(e["value"]))
            return vals

        return ForecastSlices(
            humidity_values=extract_values("relativeHumidity"),
            temperature_values=extract_values("temperature"),
            rain_probability_values=extract_values("probabilityOfPrecipitation"),
        )


def probability_for_market(market: WeatherMarket, slices: ForecastSlices) -> float:
    if market.metric == WeatherMetric.HUMIDITY:
        values = slices.humidity_values
    elif market.metric == WeatherMetric.TEMPERATURE:
        values = slices.temperature_values
    else:
        values = slices.rain_probability_values

    if not values:
        return 0.0
    if market.direction == MarketDirection.ABOVE and market.lower is not None:
        return len([v for v in values if v > market.lower]) / len(values)
    if market.direction == MarketDirection.BELOW and market.upper is not None:
        return len([v for v in values if v < market.upper]) / len(values)
    if market.direction == MarketDirection.BETWEEN and market.lower is not None and market.upper is not None:
        return len([v for v in values if market.lower <= v <= market.upper]) / len(values)
    if market.direction == MarketDirection.EVENT:
        return max(values) / 100.0 if market.metric == WeatherMetric.RAIN else min(1.0, sum(values) / len(values) / 100.0)
    return 0.0
