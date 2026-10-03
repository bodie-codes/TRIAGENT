import os
import httpx
from dotenv import load_dotenv
from triage import TriageResult

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URGENCY_ICON = {"low": "🟢", "medium": "🟡", "high": "🔴"}


# Sends a short alert about a new message to Telegram
def send_alert(result: TriageResult, message_id: int) -> bool:
    if not TOKEN or not CHAT_ID:
        return False

    text = (
        f"{URGENCY_ICON[result.urgency]} New {result.category} (#{message_id})\n"
        f"From: {result.sender_name or 'unknown'}\n"
        f"Urgency: {result.urgency}\n\n"
        f"{result.summary}"
    )

    response = httpx.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )
    return response.status_code == 200