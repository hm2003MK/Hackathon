import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Spark — an adaptive entertainment career coach.
Warm, conversational, Gen-Z friendly. Ask only one question at a time.
Guide users in discovering their creative energy and career direction.
"""

def run_spark_turn(chat_history, profile, phase):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += chat_history

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=300,
        temperature=0.8
    )

    # FIXED: message is an object, not a dict
    spark_reply = response.choices[0].message.content

    return spark_reply, profile, phase, False



