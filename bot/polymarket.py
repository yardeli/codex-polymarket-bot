from __future__ import annotations

import json
from pathlib import Path

from bot.models import TradeDecision, WeatherMarket


class PolymarketClient:
    """
    Adapter scaffold.

    - `load_weather_markets` can be switched to authenticated market discovery.
    - `execute_order` can be switched to authenticated CLOB order placement.
    """

    def __init__(self, markets_file: str) -> None:
        self.markets_file = Path(markets_file)

    def load_weather_markets(self) -> list[WeatherMarket]:
        if not self.markets_file.exists():
            return []
        payload = json.loads(self.markets_file.read_text())
        return [WeatherMarket(**row) for row in payload]

    def execute_order(self, trade: TradeDecision, dry_run: bool = True) -> dict:
        if dry_run:
            return {"status": "simulated", "trade": trade.__dict__}

        # TODO: Implement real authenticated order placement against your chosen Polymarket API/client.
        return {"status": "not_implemented", "trade": trade.__dict__}
