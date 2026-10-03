import os
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


# One row in the "messages" table = one processed message
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    original_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(20))
    urgency: Mapped[str] = mapped_column(String(10))
    sender_name: Mapped[Optional[str]] = mapped_column(String(200))
    order_number: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(50))
    draft_reply: Mapped[Optional[str]] = mapped_column(Text)


# Creates the table in the database if it doesn't exist yet
def create_tables():
    Base.metadata.create_all(engine)