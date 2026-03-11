import tempfile
import unittest
from pathlib import Path

from bot.monitor import EventStore


class EventStoreTests(unittest.TestCase):
    def test_append_and_read_recent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            store = EventStore(str(path))
            store.append("cycle", {"signals": 2})
            events = store.read_recent(10)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["type"], "cycle")
            self.assertEqual(events[0]["payload"]["signals"], 2)


if __name__ == "__main__":
    unittest.main()
