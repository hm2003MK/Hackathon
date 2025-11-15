import json
import boto3
from botocore.exceptions import ClientError

# ===============================================
# AWS Bedrock Client
# ===============================================
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


# ✔ VALID Nova model
MODEL_ID = "amazon.nova-micro-v1:0"

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
            profile["memory"][mk] = val
        elif isinstance(val, set):
            profile["memory"][mk] = list(val)
        else:
            profile["memory"][mk] = []

    # IMPORTANT FIX
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

    def add_unique(lst, item):
        if item not in lst:
            lst.append(item)

    if any(k in text for k in ["video", "tiktok", "film", "editing", "camera"]):
        add_unique(mem["mediums"], "video")

    if any(k in text for k in ["dance", "choreo"]):
        add_unique(mem["interests"], "dance")

    if any(k in text for k in ["music", "beat", "producer"]):
        add_unique(mem["interests"], "music")

    if any(k in text for k in ["organize", "team", "lead"]):
        add_unique(mem["skills"], "leadership")

    if "dream" in text or "goal" in text:
        add_unique(mem["goals"], user_message)

    return profile


# ============================================================
# LLM TURN (Nova `converse` API)
# ============================================================
def run_llm_conversation_turn(chat_history, profile, phase):
    """One conversational turn using Amazon Titan Text Premier."""

    profile = ensure_profile_structure(profile)

    # Convert memory fields to JSON-safe lists
    safe_memory = {
        "interests": list(profile["memory"]["interests"]),
        "skills": list(profile["memory"]["skills"]),
        "mediums": list(profile["memory"]["mediums"]),
        "goals": list(profile["memory"]["goals"]),
    }

    # ---------------------------------------------------------
    # Build a Titan-compatible text prompt (NO Nova schema)
    # ---------------------------------------------------------
    prompt_text = "System: " + SYSTEM_PROMPT.strip() + "\n\n"

    prompt_text += "Assistant: " + json.dumps({
        "profile": profile,
        "memory": safe_memory,
        "phase": phase
    }) + "\n\n"

    # Add chat history
    for msg in chat_history:
        if msg["role"] == "user":
            prompt_text += f"User: {msg['content']}\n"
        else:
            prompt_text += f"Assistant: {msg['content']}\n"

    prompt_text += "\nAssistant:"

    # ---------------------------------------------------------
    # Titan Text Premier invocation
    # ---------------------------------------------------------
    response = bedrock.invoke_model(
        modelId="amazon.titan-text-premier-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": prompt_text,
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "temperature": 0.8,
                "topP": 0.9
            }
        })
    )

    resp = json.loads(response["body"].read())
    spark_text = resp["results"][0]["outputText"]

    return spark_text, profile, phase, False


# ============================================================
# MAIN ENTRY FOR STREAMLIT
# ============================================================
def run_spark_turn(chat_history, profile, phase):
    profile = ensure_profile_structure(profile)
    return run_llm_conversation_turn(chat_history, profile, phase)



