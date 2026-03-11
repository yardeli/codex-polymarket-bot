from __future__ import annotations

import json
from urllib.request import Request, urlopen


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = json.dumps({"chat_id": self.chat_id, "text": text}).encode("utf-8")
        req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=15.0):
            return
