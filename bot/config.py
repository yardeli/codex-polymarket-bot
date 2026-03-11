from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    dry_run: bool
    scan_interval_seconds: int
    edge_threshold: float
    max_stake_per_trade: float
    max_open_trades: int
    telegram_bot_token: str
    telegram_chat_id: str
    polymarket_api_base: str
    polymarket_private_key: str
    polymarket_proxy_address: str
    markets_file: str
    events_file: str
    dashboard_host: str
    dashboard_port: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            dry_run=_bool("DRY_RUN", True),
            scan_interval_seconds=int(os.getenv("SCAN_INTERVAL_SECONDS", "300")),
            edge_threshold=float(os.getenv("EDGE_THRESHOLD", "0.12")),
            max_stake_per_trade=float(os.getenv("MAX_STAKE_PER_TRADE", "80")),
            max_open_trades=int(os.getenv("MAX_OPEN_TRADES", "12")),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            polymarket_api_base=os.getenv("POLYMARKET_API_BASE", "https://clob.polymarket.com"),
            polymarket_private_key=os.getenv("POLYMARKET_PRIVATE_KEY", ""),
            polymarket_proxy_address=os.getenv("POLYMARKET_PROXY_ADDRESS", ""),
            markets_file=os.getenv("MARKETS_FILE", "markets.sample.json"),
            events_file=os.getenv("EVENTS_FILE", "runtime/events.jsonl"),
            dashboard_host=os.getenv("DASHBOARD_HOST", "0.0.0.0"),
            dashboard_port=int(os.getenv("DASHBOARD_PORT", "8080")),
        )
