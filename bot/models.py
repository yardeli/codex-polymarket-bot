from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WeatherMetric(str, Enum):
    HUMIDITY = "humidity"
    TEMPERATURE = "temperature"
    RAIN = "rain"


class MarketDirection(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    BETWEEN = "between"
    EVENT = "event"


@dataclass(slots=True)
class WeatherMarket:
    market_id: str
    city: str
    lat: float
    lon: float
    metric: WeatherMetric
    direction: MarketDirection
    lower: float | None
    upper: float | None
    implied_probability: float
    price_cents: float


@dataclass(slots=True)
class Signal:
    market_id: str
    city: str
    metric: WeatherMetric
    model_probability: float
    implied_probability: float
    edge: float
    suggested_price_cents: float


@dataclass(slots=True)
class TradeDecision:
    market_id: str
    side: str
    size_usd: float
    limit_price_cents: float
    reason: str
