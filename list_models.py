import boto3
from dotenv import load_dotenv

load_dotenv()

def list_models():
    client = boto3.client(
        "bedrock",
        region_name="us-east-1"
    )

    response = client.list_foundation_models()

    anthropic_models = [
        model["modelId"]
        for model in response["modelSummaries"]
        if model["providerName"] == "Anthropic"
    ]

    # for model in response["modelSummaries"]:
    #     print(model["modelId"])
    for model_id in anthropic_models:
        print(model_id)
    
def list_inferences():
    client = boto3.client(
        "bedrock",
        region_name="us-east-1"
    )

    response = client.list_inference_profiles()

    for profile in response["inferenceProfileSummaries"]:
        print(profile["inferenceProfileId"])
        
def main():
    list_inferences()
    
if __name__ == "__main__":
    main()