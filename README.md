# NOAA-Driven Polymarket Weather Bot

A weather-only trading bot that follows the strategy in your prompt:

- Trades **only weather markets**.
- Uses **NOAA/NWS forecast data** (no news, no charting, no opinions).
- Looks for **forecast vs market-pricing lag**.
- Sends **Telegram alerts** for trade actions.
- Includes **live terminal watcher** and **web dashboard** to monitor activity.

## What you can run

### 1) Bot trader loop

```bash
python -m bot.main
```

### 2) Single cycle

```bash
python -m bot.main --once
```

### 3) Terminal live monitor

```bash
python -m bot.main --watch-terminal
```

### 4) Web dashboard

```bash
python -m bot.main --serve-web
# open http://localhost:8080
```

The dashboard reads from `runtime/events.jsonl` and refreshes every 2 seconds.

## Strategy summary

1. Pull NOAA/NWS forecast data for configured cities.
2. Evaluate weather contracts (humidity, rain, temperature brackets).
3. Convert forecasts into a model probability for each market.
4. Compare model probability to market implied probability.
5. Trade when edge >= `EDGE_THRESHOLD`.
6. Write every scan/signal/trade into the event log.

## Environment variables

See `.env.example`.

Important values:

- `DRY_RUN=true` for safety.
- `MARKETS_FILE=markets.sample.json` to define weather markets.
- `EVENTS_FILE=runtime/events.jsonl` for monitor output.
- `DASHBOARD_PORT=8080` for web viewer.

## Notes

- `bot/polymarket.py` is the execution adapter boundary.
- Dry-run is fully wired; live authenticated order placement remains a TODO in the adapter method.
