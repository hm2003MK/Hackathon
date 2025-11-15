# spark_conversation.py
import os
import json
from groq import Groq

# ============================================================
# GROQ CLIENT
# ============================================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_ID = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are Spark — an adaptive entertainment career coach.
Warm, friendly, Gen-Z conversational tone.
Ask ONE question at a time.
Your goal: gather enough info to match the user to top 3 entertainment careers.
STOP asking questions once you have enough info.
"""


# ============================================================
# PROFILE NORMALIZATION (exported)
# ============================================================
def ensure_profile_structure(profile):
    """Ensure the Spark profile has correct structure."""
    if not isinstance(profile, dict):
        profile = {}

    fields = [
        "interests", "mediums", "strengths", "work_style",
        "environment", "experience", "tools", "goals",
        "preferences", "vibe_summary"
    ]

    for f in fields:
        if f not in profile:
            profile[f] = [] if f != "vibe_summary" else ""

        if isinstance(profile[f], set):
            profile[f] = list(profile[f])

        if f != "vibe_summary" and not isinstance(profile[f], list):
            profile[f] = []

    # Memory block
    if "memory" not in profile or not isinstance(profile["memory"], dict):
        profile["memory"] = {}

    for key in ["interests", "skills", "mediums", "goals"]:
        val = profile["memory"].get(key)
        profile["memory"][key] = list(val) if isinstance(val, (list, set)) else []

    # Persona scoring seeds
    if "persona_seeds" not in profile:
        profile["persona_seeds"] = {}

    for s in [
        "movement_expression", "visual_storytelling", "sound_design",
        "narrative_thinking", "creative_leadership", "aesthetic_sense",
        "technical_builder"
    ]:
        if s not in profile["persona_seeds"]:
            profile["persona_seeds"][s] = 0

    return profile


# ============================================================
# TRAIT COMPLETENESS CHECK
# ============================================================
def has_enough_data(traits):
    """Decide when Spark stops asking questions."""
    interests = traits.get("interests", {})
    skills = traits.get("transferable_skills", {})
    signals = traits.get("passion_signals", [])

    if len(interests) >= 2:
        return True
    if len(skills) >= 2:
        return True
    if len(signals) >= 3:
        return True

    return False


# ============================================================
# MAIN SPARK TURN (exported)
# ============================================================
def run_spark_turn(chat_history, profile, phase):
    profile = ensure_profile_structure(profile)

    # Build Groq messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history)

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    spark_reply = response.choices[0].message.content

    # Extract traits to decide if Spark should end
    from match_student_to_careers import extract_traits

    user_text = " ".join(
        m["content"] for m in chat_history if m["role"] == "user"
    )

    traits_chat = [
        {"role": "assistant", "content": "You are Spark, a creative career coach."},
        {"role": "user", "content": user_text},
    ]

    traits = extract_traits(traits_chat)
    ready = has_enough_data(traits)

    return spark_reply, profile, phase, ready


# ============================================================
# EXPORTED SYMBOLS
# ============================================================
__all__ = ["run_spark_turn", "ensure_profile_structure"]





