import logging
import urllib.request
import urllib.parse
import json

from atdd_orchestrator.domain.ports import Notifier
from atdd_orchestrator.domain.story import Story
from atdd_orchestrator.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _send(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured — TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing")
        return
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    url = _API_URL.format(token=TELEGRAM_BOT_TOKEN)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                log.warning("Telegram responded %s", resp.status)
    except Exception as exc:
        log.warning("Error sending to Telegram: %s", exc)


class TelegramNotifier(Notifier):
    def pipeline_started(self, story: Story) -> None:
        _send(
            f"▶ <b>{story.id}</b> — {story.title}\n"
            f"Pipeline started · sprint: {story.sprint}"
        )

    def story_done(self, story: Story) -> None:
        _send(
            f"✅ <b>{story.id}</b> — {story.title}\n"
            f"Story completed · sprint: {story.sprint}"
        )
