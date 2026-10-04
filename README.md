# TRIAGENT

**AI that reads, sorts and answers your inbox.**

[Live demo](https://triagent-d9pg.onrender.com/demo) · [API docs](https://triagent-d9pg.onrender.com/docs)

<!-- Až budeš mít screenshot, nahraj ho do složky docs/ a odkomentuj další řádek:
![TRIAGENT demo](docs/demo.png)
-->

TRIAGENT takes an incoming customer message, understands it, sorts it, drafts a reply and alerts the team. All in a few seconds, with every step visible live in the demo.

## What it does

For every message it receives, TRIAGENT:

1. **Reads and sorts it.** It extracts the category, urgency, sender name, order number, a short summary and the language of the message (it also works with non-English messages, for example Czech).
2. **Drafts a reply** in the language of the sender.
3. **Saves the result** to a PostgreSQL database.
4. **Sends an alert** to the team (Telegram). Messages classified as spam are skipped.

```mermaid
flowchart LR
    A[Incoming message] --> B[Triage: category, urgency, summary]
    B --> C[Draft reply]
    C --> D[(PostgreSQL)]
    D --> E[Team alert, skipped for spam]
```

## Live demo

Open the [demo page](https://triagent-d9pg.onrender.com/demo), paste a message (or pick an example: complaint, inquiry, Czech invoice or spam) and watch every step happen in real time.

> The demo runs on a free server that goes to sleep when nobody uses it. The first request can take up to a minute while it wakes up. The public demo also has rate limits per visitor.

## API

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/demo` | Interactive demo page |
| `POST` | `/process` | Processes one message and returns everything at once |
| `POST` | `/process/stream` | Same, but streams every step live (Server-Sent Events) |
| `GET` | `/messages?key=...` | The 20 newest saved messages (admin key required) |

Messages must be between 5 and 2000 characters.

```bash
curl -X POST https://triagent-d9pg.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, my order arrived damaged and I would like a refund."}'
```

The response contains the saved message `id`, the `triage` result (category, urgency, sender name, order number, summary, language) and a `draft_reply`.

Interactive API documentation is generated automatically at `/docs`.

## Tech stack

- **Python** and **FastAPI** (API, validation with Pydantic)
- **LangChain** with the **Google Gemini API** (classification and reply drafting)
- **PostgreSQL** with **SQLAlchemy**
- **Docker** / Docker Compose
- Hosted on **Render** (server) and **Neon** (database)

## Run locally

```bash
git clone https://github.com/bodie-codes/TRIAGENT.git
cd TRIAGENT
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
ADMIN_KEY=choose-a-long-random-string
GEMINI_API_KEY=your-google-gemini-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

Start the server:

```bash
uvicorn main:app --reload
```

Then open <http://localhost:8000/demo>.

A `docker-compose.yml` is included for running the stack in containers:

```bash
docker compose up --build
```

## Project structure

| File | Purpose |
|---|---|
| `main.py` | FastAPI app and endpoints |
| `triage.py` | Message classification and reply drafting |
| `database.py` | Database connection and the `Message` model |
| `notify.py` | Team alerts |
| `limits.py` | Rate limiting per visitor |
| `demo.html` | Live demo page |

## Author

Built by **Bodie** · [bodiecodes.com](https://www.bodiecodes.com) · [LinkedIn](https://www.linkedin.com/in/bodiecodes)
