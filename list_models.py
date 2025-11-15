import boto3
import json

bedrock = boto3.client("bedrock", region_name="us-east-1")

resp = bedrock.list_foundation_models()

print("\nAVAILABLE MODELS:\n")
for m in resp["modelSummaries"]:
    print("-", m["modelId"])
