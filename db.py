import boto3
import uuid
from datetime import datetime

TABLE_NAME = "spark_users"

dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-2"  # Ohio region
)

table = dynamodb.Table(TABLE_NAME)


def create_user():
    user_id = str(uuid.uuid4())

    item = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "answers": {},
        "traits": {},
        "persona": {},
        "matches": [],
        "saved_careers": []
    }

    table.put_item(Item=item)
    return user_id


def get_user(user_id):
    response = table.get_item(Key={"user_id": user_id})
    return response.get("Item")


def update_user(user_id, data: dict):
    data["updated_at"] = datetime.utcnow().isoformat()

    update_expr = "SET " + ", ".join(f"{k}= :{k}" for k in data.keys())
    values = {f":{k}": v for k, v in data.items()}

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=values
    )


def add_saved_career(user_id, title, score):
    user = get_user(user_id)
    saved = user.get("saved_careers", [])
    saved.append({"title": title, "score": float(score)})

    update_user(
        user_id,
        {"saved_careers": saved}
    )
