# spark_conversation.py
import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_ID = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are Spark — an adaptive entertainment career coach.
Warm, friendly, Gen-Z conversational tone.
Ask ONE question at a time.
Your goal: gather enough info to match the user to top 3 entertainment careers.
STOP asking questions once you have enough info.
When you are ready, simply output the 3 careers directly.
"""


# ============================================================
# Detect if Spark should stop talking + produce careers
# ============================================================
def conversation_is_complete(reply: str):
    triggers = [
        "here are three careers",
        "here are 3 careers",
        "top 3 careers",
        "i've got three careers",
        "based on our chat",
        "3 entertainment careers",
        "three entertainment careers"
    ]
    return any(t in reply.lower() for t in triggers)


# ============================================================
# Main Groq conversation turn
# ============================================================
def run_spark_turn(chat_history, profile, phase):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    spark_reply = response.choices[0].message.content

    # Tell app when to summarize/match
    ready = conversation_is_complete(spark_reply)

    return spark_reply, profile, phase, ready


# ============================================================
# Export symbols
# ============================================================
__all__ = ["run_spark_turn", "conversation_is_complete"]




