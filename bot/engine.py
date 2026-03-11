from __future__ import annotations

from urllib.error import URLError

from bot.models import Signal, TradeDecision
from bot.monitor import EventStore
from bot.noaa import NoaaClient, probability_for_market
from bot.polymarket import PolymarketClient
from bot.telegram import TelegramAlerter


class WeatherTradingEngine:
    def __init__(
        self,
        noaa: NoaaClient,
        poly: PolymarketClient,
        alerts: TelegramAlerter,
        edge_threshold: float,
        max_stake_per_trade: float,
        dry_run: bool,
        event_store: EventStore,
    ) -> None:
        self.noaa = noaa
        self.poly = poly
        self.alerts = alerts
        self.edge_threshold = edge_threshold
        self.max_stake_per_trade = max_stake_per_trade
        self.dry_run = dry_run
        self.event_store = event_store

    def scan_signals(self) -> list[Signal]:
        markets = self.poly.load_weather_markets()
        signals: list[Signal] = []

        for market in markets:
            try:
                slices = self.noaa.get_slices_48h(market.lat, market.lon)
            except URLError as exc:
                msg = f"[WEATHER BOT] NOAA fetch failed for {market.city}: {exc}"
                self.alerts.send(msg)
                self.event_store.append("noaa_error", {"city": market.city, "error": str(exc)})
                continue

            model_p = probability_for_market(market, slices)
            edge = model_p - market.implied_probability
            self.event_store.append(
                "market_scan",
                {
                    "market_id": market.market_id,
                    "city": market.city,
                    "model_probability": round(model_p, 4),
                    "implied_probability": round(market.implied_probability, 4),
                    "edge": round(edge, 4),
                },
            )

            if edge >= self.edge_threshold:
                signal = Signal(
                    market_id=market.market_id,
                    city=market.city,
                    metric=market.metric,
                    model_probability=model_p,
                    implied_probability=market.implied_probability,
                    edge=edge,
                    suggested_price_cents=min(99.0, model_p * 100.0),
                )
                signals.append(signal)
                self.event_store.append_any("signal", signal)

        return signals

    def execute(self, signals: list[Signal]) -> list[dict]:
        out: list[dict] = []
        for s in signals:
            trade = TradeDecision(
                market_id=s.market_id,
                side="buy_yes",
                size_usd=self.max_stake_per_trade,
                limit_price_cents=s.suggested_price_cents,
                reason=f"NOAA edge {s.edge:.2%} ({s.model_probability:.2%} vs mkt {s.implied_probability:.2%})",
            )
            result = self.poly.execute_order(trade, dry_run=self.dry_run)
            out.append(result)
            self.event_store.append("trade", {"trade": trade.__dict__, "result": result})
            self.alerts.send(
                f"[WEATHER BOT] {s.city} {s.metric.value} | edge={s.edge:.2%} | trade={trade.size_usd:.2f} @ {trade.limit_price_cents:.1f}c | status={result['status']}"
            )
        return out
