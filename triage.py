import os
from typing import Literal, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
llm = ChatGoogleGenerativeAI(model=os.getenv("AI_MODEL"), temperature=0)
backup_llm = ChatGoogleGenerativeAI(model=os.getenv("BACKUP_MODEL"), temperature=0)

# Name of the business that "uses" Triagent in the demo
BUSINESS_NAME = "Demo Company"


# The "form" the AI has to fill in
class TriageResult(BaseModel):
    category: Literal["inquiry", "complaint", "invoice", "spam"] = Field(description="What kind of message this is")
    urgency: Literal["low", "medium", "high"] = Field(description="How urgent the message is")
    sender_name: Optional[str] = Field(description="Name of the sender exactly as written in the message, including accents like á, č, ř, if mentioned")
    order_number: Optional[str] = Field(description="Order or invoice number, if mentioned")
    summary: str = Field(description="One-sentence summary of what the sender wants, in English")
    language: str = Field(description="Language the message is written in, e.g. English, Czech")


triage_llm = llm.with_structured_output(TriageResult).with_fallbacks(
    [backup_llm.with_structured_output(TriageResult)]
)
reply_llm = llm.with_fallbacks([backup_llm])


# Step 1: sort the message
def triage(message: str) -> TriageResult:
    return triage_llm.invoke(
        "You are an assistant that sorts incoming business emails. "
        "Read this message carefully and fill in all the fields.\n\n" + message
    )


# Step 2: write a reply (no reply for spam)
def draft_reply(message: str, result: TriageResult) -> Optional[str]:
    if result.category == "spam":
        return None

    answer = reply_llm.invoke(
        f"You work in customer support at {BUSINESS_NAME}. "
        f"Write a short, friendly reply to the customer's message below.\n"
        f"Rules:\n"
        f"- Write the reply in {result.language}, the same language the customer used.\n"
        f"- Address the customer by name if it is known.\n"
        f"- Never invent prices, dates or promises. If something needs to be checked, "
        f"say that the team will get back to them.\n"
        f"- Sign off as the {BUSINESS_NAME} team, written in the same language as the reply.\n"
        f"- Return only the reply text, no subject line.\n\n"
        f"Message category: {result.category}\n"
        f"Customer message:\n{message}"
    )
    return answer.text


# Test: runs only when you start this file directly
if __name__ == "__main__":
    test_messages = [
        "Hi, I ordered a coffee machine from you on September 3rd and it arrived broken. I want to return it ASAP. John Smith, order #4521.",
        "Dobrý den, zajímalo by mě, kolik by stála výroba webových stránek pro naši kavárnu. Petra Nováková",
        "CONGRATULATIONS!!! You have won $1,000,000. Click here to claim your prize now!",
    ]

    for msg in test_messages:
        result = triage(msg)
        print(result.model_dump_json(indent=2))

        reply = draft_reply(msg, result)
        print("\nDRAFT REPLY:")
        print(reply if reply else "(no reply – spam)")
        print("-" * 40)