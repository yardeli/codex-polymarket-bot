from __future__ import annotations

import argparse
import time

from bot.config import Settings
from bot.engine import WeatherTradingEngine
from bot.monitor import EventStore, watch_terminal
from bot.noaa import NoaaClient
from bot.polymarket import PolymarketClient
from bot.telegram import TelegramAlerter
from bot.web import serve_web_dashboard


def run_once(settings: Settings, event_store: EventStore) -> None:
    noaa = NoaaClient()
    try:
        engine = WeatherTradingEngine(
            noaa=noaa,
            poly=PolymarketClient(settings.markets_file),
            alerts=TelegramAlerter(settings.telegram_bot_token, settings.telegram_chat_id),
            edge_threshold=settings.edge_threshold,
            max_stake_per_trade=settings.max_stake_per_trade,
            dry_run=settings.dry_run,
            event_store=event_store,
        )
        signals = engine.scan_signals()
        engine.execute(signals)
        event_store.append("cycle", {"signals": len(signals), "dry_run": settings.dry_run})
        print(f"signals={len(signals)} dry_run={settings.dry_run}")
    finally:
        noaa.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one scan cycle")
    parser.add_argument("--watch-terminal", action="store_true", help="Tail live events in terminal")
    parser.add_argument("--serve-web", action="store_true", help="Serve browser dashboard")
    args = parser.parse_args()
    settings = Settings.from_env()
    event_store = EventStore(settings.events_file)

    if args.watch_terminal:
        watch_terminal(settings.events_file)
        return

    if args.serve_web:
        serve_web_dashboard(event_store, settings.dashboard_host, settings.dashboard_port)
        return

    if args.once:
        run_once(settings, event_store)
        return

    while True:
        run_once(settings, event_store)
        time.sleep(settings.scan_interval_seconds)


if __name__ == "__main__":
    main()
