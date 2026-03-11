from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bot.monitor import EventStore


HTML = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>Polymarket Weather Bot Live Monitor</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #0b1020; color: #dbe5ff; }
    h1 { margin-bottom: 8px; }
    .muted { color: #98a6d4; margin-bottom: 20px; }
    .card { background: #121936; border: 1px solid #24305f; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
    .type { font-weight: bold; color: #8ec5ff; }
    code { color: #b1ffd9; }
  </style>
</head>
<body>
  <h1>NOAA → Signal → Trade Live Feed</h1>
  <div class='muted'>Auto-refreshing every 2 seconds.</div>
  <div id='events'></div>
<script>
async function load() {
  const res = await fetch('/events');
  const data = await res.json();
  const root = document.getElementById('events');
  root.innerHTML = '';
  data.reverse().forEach(ev => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `<div><span class='type'>${ev.type}</span> <code>${ev.ts}</code></div><pre>${JSON.stringify(ev.payload, null, 2)}</pre>`;
    root.appendChild(div);
  });
}
load();
setInterval(load, 2000);
</script>
</body>
</html>
"""


def serve_web_dashboard(event_store: EventStore, host: str = "0.0.0.0", port: int = 8080) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                body = HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if self.path == "/events":
                payload = json.dumps(event_store.read_recent(300)).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            self.send_response(404)
            self.end_headers()

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"dashboard=http://{host}:{port}")
    server.serve_forever()
