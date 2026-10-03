import os
import httpx
from dotenv import load_dotenv
from triage import TriageResult

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URGENCY_ICON = {"low": "🟢", "medium": "🟡", "high": "🔴"}


# Builds the text of the alert (also shown on the demo page)
def build_alert_text(result: TriageResult, message_id: int) -> str:
    return (
        f"{URGENCY_ICON[result.urgency]} New {result.category} (#{message_id})\n"
        f"From: {result.sender_name or 'unknown'}\n"
        f"Urgency: {result.urgency}\n\n"
        f"{result.summary}"
    )


# Sends the alert to Telegram, returns True if it was delivered
def send_alert(text: str) -> bool:
    if not TOKEN or not CHAT_ID:
        return False

    response = httpx.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=10,
    )
    return response.status_code == 200