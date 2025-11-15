import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def embed(text):
    body = json.dumps({"inputText": text})
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )
    out = json.loads(resp["body"].read())
    return out["embedding"]


# -----------------------------------
# LOAD YOUR JSON (dict → list)
# -----------------------------------
with open("careers_midsize.json", "r") as f:
    data = json.load(f)

careers_list = data["careers"]   # this is the list you showed me

output = {}

# -----------------------------------
# BUILD EMBEDDINGS FOR EACH CAREER
# -----------------------------------
for item in careers_list:
    title = item["name"]
    category = item.get("category", "")
    desc = item.get("description", "")

    full_text = f"{title}. {desc}. Category: {category}"

    print(f"Embedding → {title}")
    emb = embed(full_text)

    output[title] = {
        "description": desc,
        "category": category,
        "embedding": emb
    }

# -----------------------------------
# SAVE NEW EMBEDDINGS
# -----------------------------------
with open("career_embeddings.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✔ DONE — Titan v2 embeddings (1024-dim) rebuilt successfully!")


