import json
import boto3

# ============================================================
# AWS Bedrock Client (correct region)
# ============================================================
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

MODEL_ID = "qwen.qwen3-235b-a22b-2507-v1:0"

SYSTEM_PROMPT = """
You are Spark — an adaptive entertainment career coach.
Warm, conversational, Gen-Z friendly. Ask only one question at a time.
Build a creative profile while chatting.
"""

# ============================================================
# PROFILE NORMALIZATION
# ============================================================
def ensure_profile_structure(profile):
    if not isinstance(profile, dict):
        profile = {}

    for k in ["interests", "mediums", "strengths", "goals"]:
        if k not in profile or not isinstance(profile[k], list):
            profile[k] = []

    if "memory" not in profile or not isinstance(profile["memory"], dict):
        profile["memory"] = {}

    for k in ["interests", "skills", "mediums", "goals"]:
        v = profile["memory"].get(k)
        profile["memory"][k] = list(v) if isinstance(v, (list, set)) else []

    if "persona_seeds" not in profile:
        profile["persona_seeds"] = {}

    for seed in [
        "movement_expression", "visual_storytelling", "sound_design",
        "narrative_thinking", "creative_leadership",
        "aesthetic_sense", "technical_builder"
    ]:
        if seed not in profile["persona_seeds"]:
            profile["persona_seeds"][seed] = 0

    return profile


# ============================================================
# QWEN TURN (invoke-model)
# ============================================================
def run_llm_conversation_turn(chat_history, profile, phase):
    profile = ensure_profile_structure(profile)

    safe_mem = {
        "interests": profile["memory"]["interests"],
        "skills": profile["memory"]["skills"],
        "mediums": profile["memory"]["mediums"],
        "goals": profile["memory"]["goals"]
    }

    # --------------------------------------------
    # Build raw text prompt for QWEN
    # --------------------------------------------
    prompt = f"System: {SYSTEM_PROMPT.strip()}\n\n"
    prompt += "Assistant profile context: " + json.dumps({
        "profile": profile,
        "memory": safe_mem,
        "phase": phase
    }) + "\n\n"

    for msg in chat_history:
        if msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        else:
            prompt += f"Assistant: {msg['content']}\n"

    prompt += "Assistant:"

    # --------------------------------------------
    # QWEN-compatible Bedrock call
    # --------------------------------------------
    body = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.8,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    output = result["output_text"]

    return output, profile, phase, False


# ============================================================
# MAIN ENTRY
# ============================================================
def run_spark_turn(chat_history, profile, phase):
    return run_llm_conversation_turn(chat_history, profile, phase)


