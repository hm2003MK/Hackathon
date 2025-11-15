# pages/1_Career_Explorer.py

import streamlit as st
import json

from theme import apply_theme
from spark_conversation import run_spark_turn, conversation_is_complete

from match_student_to_careers import (
    extract_traits,
    get_embedding,
    match_careers,
    build_report,
    career_embeddings
)

from db import update_user


# ======================================================
# THEME
# ======================================================
apply_theme()

st.markdown(
    """
    <h2 style="font-size:32px; font-weight:700; margin-bottom:4px;">
        🎤 SparkPath – Conversational Career Explorer
    </h2>
    <p style="font-size:14px; opacity:0.75; max-width:640px;">
        Chat with Spark about your interests, strengths, and creative energy.
        Spark listens, asks follow-ups, then generates a persona and top 3 careers.
    </p>
    """,
    unsafe_allow_html=True
)

# ======================================================
# STATE INIT
# ======================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "summary_ready" not in st.session_state:
    st.session_state.summary_ready = False

if "spark_results" not in st.session_state:
    st.session_state.spark_results = None

if "saved_careers" not in st.session_state:
    st.session_state.saved_careers = []

user_id = st.session_state.get("user_id")


# ======================================================
# INITIAL MESSAGE
# ======================================================
if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": (
            "Hey, I’m Spark ✨ Tell me about something creative you naturally "
            "gravitate toward—TikToks, dance, music, fashion, film, design… "
            "whatever feels most you."
        )
    })


# ======================================================
# RENDER CHAT LOG
# ======================================================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ======================================================
# USER INPUT (disabled after summary)
# ======================================================
if not st.session_state.summary_ready:
    user_input = st.chat_input("Tell Spark something about your creative world…")
else:
    user_input = None


# ======================================================
# PROCESS USER TURN
# ======================================================
if user_input:

    # add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # run Spark via Groq
    spark_reply, _, _, ready_flag = run_spark_turn(
        st.session_state.chat_history,
        profile={},   # not used in Groq version
        phase="chat"
    )

    # add Spark reply
    st.session_state.chat_history.append({"role": "assistant", "content": spark_reply})

    # determine if conversation has enough data
    if ready_flag or conversation_is_complete(spark_reply):
        st.session_state.summary_ready = True

    st.rerun()


# ======================================================
# FINAL STEP — BUILD RESULTS ONCE
# ======================================================
if st.session_state.summary_ready and st.session_state.spark_results is None:

    with st.spinner("Got it — pulling together your creative vibe… ✨"):

        # gather all user text
        user_text = " ".join(
            m["content"] for m in st.session_state.chat_history if m["role"] == "user"
        )

        # extract traits
        traits_chat = [
            {"role": "assistant", "content": "You are Spark, an entertainment career coach."},
            {"role": "user", "content": user_text},
        ]

        traits = extract_traits(traits_chat)

        # build embedding
        embedding_payload = (
            json.dumps(traits.get("interests", {})) + " " +
            json.dumps(traits.get("transferable_skills", {})) + " " +
            " ".join(traits.get("passion_signals", [])) + " " +
            user_text
        )

        emb = get_embedding(embedding_payload)
        matches = match_careers(emb, career_embeddings)

        # persona
        def infer_persona(tr, text):
            blob = (tr.get("vibe_summary", "") + " " + text).lower()

            if any(w in blob for w in ["dance", "movement", "choreo"]):
                return {"name": "The Movement Storyteller",
                        "blurb": "You express emotion through movement and rhythm."}

            if any(w in blob for w in ["camera", "film", "edit", "video"]):
                return {"name": "The Visual Storyteller",
                        "blurb": "You see stories in scenes, angles, and imagery."}

            if any(w in blob for w in ["music", "sound", "audio", "producer"]):
                return {"name": "The Music Architect",
                        "blurb": "You shape emotion through sound and audio textures."}

            if any(w in blob for w in ["write", "script", "story"]):
                return {"name": "The Story Weaver",
                        "blurb": "You craft narratives with ideas and words."}

            return {"name": "The Creative Explorer",
                    "blurb": "You’re multi-curious — Spark helps you discover your path."}

        persona = infer_persona(traits, user_text)
        report = build_report(traits, matches)

        # save results
        st.session_state.spark_results = {
            "traits": traits,
            "matches": matches,
            "persona": persona,
            "report": report,
        }

        # save to DynamoDB
        if user_id:
            update_user(
                user_id,
                {
                    "answers": {"chat_history": st.session_state.chat_history},
                    "traits": traits,
                    "persona": persona,
                    "matches": matches,
                }
            )

    st.rerun()


# ======================================================
# SHOW RESULTS (if already built)
# ======================================================
if st.session_state.spark_results:

    results = st.session_state.spark_results
    persona = results["persona"]
    matches = results["matches"]

    # 🔥 FIX: normalize persona
    if isinstance(persona, str):
        persona = {"name": persona, "blurb": ""}

    if not isinstance(persona, dict):
        persona = {"name": "Creative Explorer", "blurb": ""}

    st.markdown("## 🌟 Your Creative Identity")
    st.markdown(f"### **{persona['name']}**")
    st.markdown(persona.get("blurb", ""))

    st.markdown("## 🎯 Your Top Career Matches")

    for i, (title, score) in enumerate(matches[:3]):
        st.markdown(
            f"""
            <div class="sp-card" style="margin-bottom:14px;">
                <div class="sp-chip">Match</div>
                <h4>{title}</h4>
                <p style="opacity:0.7;">Match score: {score:.3f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ⭐ Save button
        if st.button(f"⭐ Save {title}", key=f"save_{i}"):
            st.session_state.saved_careers.append(
                {"title": title, "score": score}
            )
            st.success(f"Saved {title}!")

    st.markdown("## 📄 Full SparkPath Report")
    st.code(results["report"])

