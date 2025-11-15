# pages/1_Career_Explorer.py

import streamlit as st
import json

from theme import apply_theme
from spark_conversation import run_spark_turn
from spark_conversation import ensure_profile_structure
from db import update_user, add_saved_career

from match_student_to_careers import (
    extract_traits,
    get_embedding,
    match_careers,
    build_report,
    career_embeddings
)

# ======================================================
# JSON-SAFE CONVERTER (Fixes: "set is not JSON serializable")
# ======================================================
def make_json_safe(obj):
    """Recursively convert sets → lists for JSON serialization."""
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    return obj

# ======================================================
# APPLY THEME
# ======================================================
apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:4px;">
        🎤 SparkPath – Conversational Career Explorer
    </h2>
    <p style="font-size:14px; opacity:0.7; max-width:640px;">
        Chat with Spark about your interests, strengths, and creative energy.
        Spark will listen, ask follow-ups, and then show you a creative persona
        and some possible entertainment career paths.
    </p>
    """,
    unsafe_allow_html=True
)

# ======================================================
# SESSION STATE SETUP
# ======================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "spark_profile" not in st.session_state:
    st.session_state.spark_profile = ensure_profile_structure({
        "interests": [],
        "mediums": [],
        "strengths": [],
        "work_style": [],
        "environment": [],
        "experience": [],
        "tools": [],
        "goals": [],
        "preferences": [],
        "vibe_summary": "",
        "persona_seeds": {},
        "memory": {}
    })
else:
    st.session_state.spark_profile = ensure_profile_structure(
        st.session_state.spark_profile
    )

if "spark_phase" not in st.session_state:
    st.session_state.spark_phase = "warmup"

if "spark_ready" not in st.session_state:
    st.session_state.spark_ready = False

if "spark_results" not in st.session_state:
    st.session_state.spark_results = None

user_id = st.session_state.get("user_id")  # created in app.py

# ======================================================
# INITIAL BOT MESSAGE
# ======================================================
if not st.session_state.chat_history:
    opening = (
        "Hey, I’m Spark ✨ Tell me about something creative you naturally "
        "gravitate toward—TikToks, dance, music, fashion, film, design… "
        "whatever feels most you."
    )
    st.session_state.chat_history.append({"role": "assistant", "content": opening})

# ======================================================
# DISPLAY CHAT HISTORY
# ======================================================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ======================================================
# CHAT INPUT (disabled if summary is done)
# ======================================================
if not st.session_state.spark_ready:
    user_input = st.chat_input("Tell Spark about your creative world...")
else:
    user_input = None

if user_input:
    # 1. Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2. Run one conversational turn
    spark_text, new_profile, new_phase, ready = run_spark_turn(
        chat_history=st.session_state.chat_history,
        profile=st.session_state.spark_profile,
        phase=st.session_state.spark_phase
    )

    st.session_state.spark_profile = new_profile
    st.session_state.spark_phase = new_phase
    st.session_state.spark_ready = ready

    # 3. Show Spark’s reply
    st.session_state.chat_history.append({"role": "assistant", "content": spark_text})

    # Force rerender so new messages appear immediately
    st.experimental_rerun()

# ======================================================
# WHEN READY: RUN MATCHING ENGINE
# ======================================================
if st.session_state.spark_ready and st.session_state.spark_results is None:
    with st.spinner("Got it. Let me pull your vibe together into a SparkPath profile… ✨"):

        # Combine all user messages into one block for trait extraction
        user_text = " ".join(
            m["content"] for m in st.session_state.chat_history if m["role"] == "user"
        )

        chat_for_traits = [
            {"role": "assistant", "content": "You are Spark, an entertainment career coach."},
            {"role": "user", "content": user_text}
        ]

        traits = extract_traits(chat_for_traits)

        # -----------------------------------------
        # FIXED: convert profile to JSON-safe format
        # -----------------------------------------
        safe_profile = make_json_safe(st.session_state.spark_profile)

        # Build embedding input: structured profile + freeform text
        text_block = (
            json.dumps(safe_profile) + " " +
            json.dumps(traits.get("interests", {})) + " " +
            json.dumps(traits.get("transferable_skills", {})) + " " +
            " ".join(traits.get("passion_signals", [])) + " " +
            user_text
        )

        emb = get_embedding(text_block)
        matches = match_careers(emb, career_embeddings)

        # ---------------------
        # Persona Inference
        # ---------------------
        def infer_persona(traits_obj, combined_text: str):
            blob = (traits_obj.get("vibe_summary", "") + " " + combined_text).lower()
            if any(k in blob for k in ["dance", "movement", "choreo"]):
                return {
                    "name": "The Movement Storyteller",
                    "blurb": "You express emotion through movement and physical energy."
                }
            if any(k in blob for k in ["camera", "film", "edit", "video"]):
                return {
                    "name": "The Visual Storyteller",
                    "blurb": "You think in scenes and frames, and see stories in images."
                }
            if any(k in blob for k in ["music", "producer", "sound", "beat"]):
                return {
                    "name": "The Music Architect",
                    "blurb": "You shape feelings and stories through sound and rhythm."
                }
            if any(k in blob for k in ["write", "script", "story", "dialogue"]):
                return {
                    "name": "The Story Weaver",
                    "blurb": "You craft emotion and meaning through ideas and words."
                }
            return {
                "name": "The Creative Explorer",
                "blurb": "You’re multi-curious — SparkPath helps you test which paths fit."
            }

        persona = infer_persona(traits, user_text)
        report = build_report(traits, matches)

        # Store everything in session
        st.session_state.spark_results = {
            "traits": traits,
            "matches": matches,
            "persona": persona,
            "report": report,
        }

        # Save to DynamoDB
        if user_id is not None:
            update_user(
                user_id,
                {
                    "answers": {"chat_history": st.session_state.chat_history},
                    "traits": traits,
                    "persona": persona,
                    "matches": matches,
                    "profile": st.session_state.spark_profile,
                }
            )
