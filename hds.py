import boto3
import json

# 1. Client to list models (control plane)
bedrock_control = boto3.client("bedrock", region_name="us-east-1")

# 2. Client to call models (runtime)
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

try:
    # Test listing models
    models = bedrock_control.list_foundation_models()
    print("SUCCESS! Models available:")
    for m in models["modelSummaries"][:5]:
        print("-", m["modelId"])
except Exception as e:
    print("ERROR listing models:")
    print(e)

print("\n---\n")

# Test a simple embedding call
try:
    body = json.dumps({"inputText": "hello"})
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body
    )
    print("SUCCESS! Runtime call worked.")
except Exception as e:
    print("ERROR calling runtime:")
    print(e)
