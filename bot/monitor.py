from __future__ import annotations

import json
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path


class EventStore:
    def __init__(self, path: str = "runtime/events.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def append(self, event_type: str, payload: dict) -> None:
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def append_any(self, event_type: str, payload: object) -> None:
        if is_dataclass(payload):
            self.append(event_type, asdict(payload))
            return
        if isinstance(payload, dict):
            self.append(event_type, payload)
            return
        self.append(event_type, {"value": str(payload)})

    def read_recent(self, limit: int = 200) -> list[dict]:
        lines = self.path.read_text(encoding="utf-8").splitlines()
        selected = lines[-limit:]
        out: list[dict] = []
        for line in selected:
            if not line.strip():
                continue
            out.append(json.loads(line))
        return out


def watch_terminal(path: str = "runtime/events.jsonl", poll_seconds: float = 1.0) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("")

    print(f"[watch] watching {p}")
    with p.open("r", encoding="utf-8") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(poll_seconds)
                continue
            row = json.loads(line)
            ts = row.get("ts", "")
            kind = row.get("type", "")
            payload = row.get("payload", {})
            print(f"[{ts}] {kind}: {payload}")
