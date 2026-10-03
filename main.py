import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session
from triage import triage, draft_reply, TriageResult
from database import engine, Message, create_tables
from notify import send_alert


# When the server starts, make sure the table exists
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Triagent API",
    description="AI that reads, sorts and answers your inbox.",
    lifespan=lifespan,
)


# What the server receives
class IncomingMessage(BaseModel):
    message: str


# What the server sends back after processing
class ProcessedMessage(BaseModel):
    id: int
    triage: TriageResult
    draft_reply: Optional[str]


# How a saved message looks in the list
class SavedMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    received_at: datetime
    category: str
    urgency: str
    sender_name: Optional[str]
    summary: str
    draft_reply: Optional[str]


# Saves one processed message into the database and returns its id
def save_message(text: str, result: TriageResult, reply: Optional[str]) -> int:
    with Session(engine) as session:
        record = Message(
            original_text=text,
            category=result.category,
            urgency=result.urgency,
            sender_name=result.sender_name,
            order_number=result.order_number,
            summary=result.summary,
            language=result.language,
            draft_reply=reply,
        )
        session.add(record)
        session.commit()
        return record.id


# One live update ("event") sent to the browser
def event(step: str, status: str, data: Optional[dict] = None) -> str:
    return f"data: {json.dumps({'step': step, 'status': status, 'data': data or {}})}\n\n"


# Check that the server is running
@app.get("/")
def home():
    return {"status": "Triagent is running"}


# Demo page
@app.get("/demo")
def demo():
    return FileResponse("demo.html")


# Main door: process a message and return everything at once
@app.post("/process")
def process(incoming: IncomingMessage) -> ProcessedMessage:
    result = triage(incoming.message)
    reply = draft_reply(incoming.message, result)
    saved_id = save_message(incoming.message, result, reply)
    if result.category != "spam":
        send_alert(result, saved_id)
    return ProcessedMessage(id=saved_id, triage=result, draft_reply=reply)


# Live door: process a message and report every step as it happens
@app.post("/process/stream")
def process_stream(incoming: IncomingMessage):
    def run():
        step = "received"
        try:
            yield event("received", "done", {"length": len(incoming.message)})

            step = "triage"
            yield event(step, "working")
            result = triage(incoming.message)
            yield event(step, "done", result.model_dump())

            step = "reply"
            yield event(step, "working")
            reply = draft_reply(incoming.message, result)
            yield event(step, "done", {"draft_reply": reply})

            step = "save"
            yield event(step, "working")
            saved_id = save_message(incoming.message, result, reply)
            yield event(step, "done", {"id": saved_id})

            step = "notify"
            if result.category == "spam":
                yield event(step, "done", {"skipped": True})
            else:
                yield event(step, "working")
                sent = send_alert(result, saved_id)
                yield event(step, "done", {"sent": sent})
        except Exception:
            yield event(step, "failed")

    return StreamingResponse(run(), media_type="text/event-stream")


# List of the 20 newest saved messages
@app.get("/messages")
def list_messages() -> list[SavedMessage]:
    with Session(engine) as session:
        rows = session.scalars(
            select(Message).order_by(Message.id.desc()).limit(20)
        ).all()
        return [SavedMessage.model_validate(row) for row in rows]