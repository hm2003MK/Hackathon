import json
import boto3
from botocore.exceptions import ClientError

# ===============================================
# AWS Bedrock Client
# ===============================================
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

# ✔ VALID Nova model
MODEL_ID = "amazon.nova-lite-v1:0"

# ===============================================
# SYSTEM PROMPT
# ===============================================
SYSTEM_PROMPT = """
You are Spark — an adaptive entertainment career coach. 
You ask short, friendly, conversational questions. 
You remember what the user says and build a creative profile.
You never ask more than one question at a time.
You speak with warmth and Gen Z-friendly energy.
"""

# ============================================================
# PROFILE SCHEMA NORMALIZER
# ============================================================
def ensure_profile_structure(profile):
    """Ensures all required fields exist and prevents KeyErrors."""

    if not isinstance(profile, dict):
        profile = {}

    REQUIRED_LIST_FIELDS = [
        "interests", "mediums", "strengths", "work_style",
        "environment", "experience", "tools",
        "goals", "preferences"
    ]

    for key in REQUIRED_LIST_FIELDS:
        if key not in profile or not isinstance(profile[key], list):
            profile[key] = []

    if "vibe_summary" not in profile:
        profile["vibe_summary"] = ""

    if "persona_seeds" not in profile:
        profile["persona_seeds"] = {}

    SEED_KEYS = [
        "movement_expression",
        "visual_storytelling",
        "sound_design",
        "narrative_thinking",
        "creative_leadership",
        "aesthetic_sense",
        "technical_builder",
    ]

    for s in SEED_KEYS:
        if s not in profile["persona_seeds"]:
            profile["persona_seeds"][s] = 0

    if "memory" not in profile or not isinstance(profile["memory"], dict):
        profile["memory"] = {}

    MEMORY_KEYS = ["interests", "skills", "mediums", "goals"]

    for mk in MEMORY_KEYS:
        val = profile["memory"].get(mk)
        if isinstance(val, list):
            profile["memory"][mk] = set(val)
        elif isinstance(val, set):
            pass
        else:
            profile["memory"][mk] = set()

    return profile

# ============================================================
# ADAPTIVE PERSONA SEEDS
# ============================================================
def update_persona_seeds(profile, user_message: str):
    text = user_message.lower()
    seeds = profile["persona_seeds"]

    mapping = {
        "dance": ("movement_expression", 3),
        "choreo": ("movement_expression", 3),
        "video": ("visual_storytelling", 3),
        "film": ("visual_storytelling", 3),
        "editing": ("visual_storytelling", 3),
        "music": ("sound_design", 3),
        "beat": ("sound_design", 3),
        "producer": ("sound_design", 3),
        "write": ("narrative_thinking", 3),
        "story": ("narrative_thinking", 3),
        "script": ("narrative_thinking", 3),
        "organize": ("creative_leadership", 2),
        "team": ("creative_leadership", 2),
        "fashion": ("aesthetic_sense", 3),
        "style": ("aesthetic_sense", 3),
        "tech": ("technical_builder", 2),
        "software": ("technical_builder", 2)
    }

    for keyword, (seed, pts) in mapping.items():
        if keyword in text:
            seeds[seed] += pts

    return profile

# ============================================================
# MEMORY EXTRACTION
# ============================================================
def update_memory(profile, user_message: str):
    text = user_message.lower()
    mem = profile["memory"]

    if any(k in text for k in ["video", "tiktok", "film", "editing", "camera"]):
        mem["mediums"].add("video")

    if any(k in text for k in ["dance", "choreo"]):
        mem["interests"].add("dance")

    if any(k in text for k in ["music", "beat", "producer"]):
        mem["interests"].add("music")

    if any(k in text for k in ["organize", "team", "lead"]):
        mem["skills"].add("leadership")

    if "dream" in text or "goal" in text:
        mem["goals"].add(user_message)

    return profile


# ============================================================
# LLM TURN (Nova `converse` API)
# ============================================================
def run_llm_conversation_turn(chat_history, profile, phase):
    """One conversational turn using Amazon Nova Lite."""

    profile = ensure_profile_structure(profile)

    # Convert sets → lists for JSON
    safe_memory = {
        "interests": list(profile["memory"]["interests"]),
        "skills": list(profile["memory"]["skills"]),
        "mediums": list(profile["memory"]["mediums"]),
        "goals": list(profile["memory"]["goals"]),
    }

    # ---------------------------------------------------------
    # Build Nova messages
    # ---------------------------------------------------------
    messages = [
        {
            "role": "system",
            "content": [{"text": SYSTEM_PROMPT}]
        },
        {
            "role": "assistant",
            "content": [{
                "text": json.dumps({
                    "profile": profile,
                    "memory": safe_memory,
                    "phase": phase
                })
            }]
        }
    ]

    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })

    # ---------------------------------------------------------
    # Bedrock Nova call (correct API)
    # ---------------------------------------------------------
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.8
        }
    )

    spark_text = response["output"]["message"]["content"][0]["text"]

    return spark_text, profile, phase, False


# ============================================================
# MAIN ENTRY FOR STREAMLIT
# ============================================================
def run_spark_turn(chat_history, profile, phase):
    profile = ensure_profile_structure(profile)
    return run_llm_conversation_turn(chat_history, profile, phase)




