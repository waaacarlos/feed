import asyncio
import json
from pathlib import Path
import feedparser
from telegram import Bot
import os
from dotenv import load_dotenv
import html

import time

load_dotenv()


class Feed:
    abs_file_path = os.path.dirname(__file__)
    STATE_FILE = Path(f'{abs_file_path}/state.json')

    def __init__(self):
        self.url = os.getenv("FEED_URL")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        self.state = self.load_state()

    # ---------- STATE ----------
    def load_state(self):
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sent_ids": []}

    def save_state(self):
        with open(self.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    # ---------- FEED ----------
    def get_new_entries(self, feed):
        new_entries = []

        for entry in feed.entries:
            entry_id = (
                entry.get("id")
                or entry.get("link")
                or entry.get("title")
            )

            if entry_id and entry_id not in self.state["sent_ids"]:
                new_entries.append((entry_id, entry))

        return new_entries

    # ---------- TELEGRAM ----------
    async def send_to_telegram(self, entry):
        title = entry.get("title", "Senza titolo")
        link = entry.get("link", "")
        description = entry.get("description", "").replace("&#8230;", "...")

        msg = f"*{title}*\n{html.unescape(description)}\n{link}"

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=msg,
            parse_mode="Markdown"
        )

    # ---------- LOOP ----------
    async def run(self):
        while True:
            if time.localtime().tm_hour >= 22 or time.localtime().tm_hour < 8:
                await asyncio.sleep(3600)
                continue
            feed = feedparser.parse(self.url)

            new_entries = self.get_new_entries(feed)

            for entry_id, entry in reversed(new_entries):
                await self.send_to_telegram(entry)
                self.state["sent_ids"].append(entry_id)

            if new_entries:
                self.save_state()

            await asyncio.sleep(3600)
