import boto3
import json
import numpy as np

# ============================================================
#  AWS BEDROCK CLIENT
# ============================================================

bedrock = boto3.Session(profile_name="AdministratorAccess-130214420636").client(
    "bedrock-runtime",
    region_name="us-east-1"
)


# ============================================================
#  TITAN TEXT EMBEDDINGS
# ============================================================

def get_embedding(text: str):
    body = json.dumps({
        "inputText": text
    })

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    out = json.loads(response["body"].read())
    return np.array(out["embedding"])


# ============================================================
#  LOAD CAREER EMBEDDINGS
# ============================================================

with open("career_embeddings.json", "r") as f:
    career_embeddings = json.load(f)

print(f"Loaded {len(career_embeddings)} career embeddings.\n")


# ============================================================
#  TRAIT EXTRACTION PROMPTS
# ============================================================

TRAIT_SYSTEM_PROMPT = """
You analyze conversations with young students and extract structured JSON 
describing their transferable skills, interests, passions, and experience.
Return ONLY JSON. No explanations.
"""

def build_trait_prompt(chat):
    transcript = ""
    for msg in chat:
        who = "Student" if msg["role"] == "user" else "Assistant"
        transcript += f"{who}: {msg['content']}\n"

    user_prompt = f"""
Analyze this conversation:

{transcript}

Return JSON in this exact format:

{{
  "transferable_skills": {{
    "communication": 0,
    "creativity": 0,
    "organization": 0,
    "leadership": 0,
    "visual_design": 0,
    "problem_solving": 0,
    "digital_fluency": 0,
    "collaboration": 0,
    "initiative": 0,
    "customer_service": 0,
    "time_management": 0
  }},
  "interests": {{
    "video": 0,
    "music": 0,
    "writing": 0,
    "performance": 0,
    "design": 0,
    "technology": 0,
    "entrepreneurship": 0
  }},
  "passion_signals": ["keyword"],
  "work_experience_summary": "string",
  "vibe_summary": "string"
}}

Return JSON ONLY.
"""
    return user_prompt


# ============================================================
#  AMAZON NOVA-MICRO — CORRECT SCHEMA
# ============================================================

def extract_traits(chat):
    user_prompt = build_trait_prompt(chat)

    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",

        # ✔ system prompt goes here
        system=[
            {"text": TRAIT_SYSTEM_PROMPT}
        ],

        # ✔ messages can ONLY be user/assistant roles
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": user_prompt}
                ]
            }
        ]
    )

    # Nova "converse" response format:
    # response["output"]["message"]["content"][0]["text"]
    output_text = response["output"]["message"]["content"][0]["text"]

    try:
        return json.loads(output_text)
    except Exception:
        print("\nERROR: Nova returned invalid JSON:\n")
        print(output_text)
        raise


# ============================================================
#  COSINE SIMILARITY
# ============================================================

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ============================================================
#  CAREER MATCHING
# ============================================================

def match_careers(student_emb, career_embeddings):
    scores = []
    for career, data in career_embeddings.items():
        score = cosine(student_emb, np.array(data["embedding"]))
        scores.append((career, round(score, 4)))
    return sorted(scores, key=lambda x: x[1], reverse=True)


# ============================================================
#  REPORT GENERATOR
# ============================================================

def build_report(traits, matches):
    top3 = matches[:3]

    return f"""
======================
✨ SPARK PATHWAY REPORT ✨
======================

Top Career Matches:
1. {top3[0][0]} (score {top3[0][1]})
2. {top3[1][0]} (score {top3[1][1]})
3. {top3[2][0]} (score {top3[2][1]})

Your Strengths:
{json.dumps(traits["transferable_skills"], indent=2)}

Your Interests:
{json.dumps(traits["interests"], indent=2)}

Your Passions:
{traits["passion_signals"]}

Work Experience Summary:
{traits["work_experience_summary"]}

Overall Vibe:
{traits["vibe_summary"]}

✨ This pathway blends your real-world experience, strengths, and interests 
with careers in the creative industry!
"""


# ============================================================
#  SAMPLE CHAT (REPLACE WITH REAL CONVERSATION)
# ============================================================

chat = [
    {"role": "assistant", "content": "Tell me something you're good at or a job you had."},
    {"role": "user", "content": "I worked at Publix as a cashier and helped customers every day."},
    {"role": "assistant", "content": "What did you enjoy most about that?"},
    {"role": "user", "content": "Talking to people and helping them solve problems."}
]


# ============================================================
#  RUN PIPELINE
# ============================================================

print("\nExtracting student traits using Amazon Nova...\n")
traits = extract_traits(chat)

print("\nTraits extracted:")
print(json.dumps(traits, indent=2))

student_text = (
    json.dumps(traits["transferable_skills"]) + " " +
    json.dumps(traits["interests"]) + " " +
    " ".join(traits["passion_signals"]) + " " +
    traits["work_experience_summary"]
)

print("\nGenerating student embedding...\n")
student_emb = get_embedding(student_text)

print("\nMatching careers...\n")
matches = match_careers(student_emb, career_embeddings)

print("\nTop 5 Matches:")
print(matches[:5])

print("\n" + build_report(traits, matches))
