import boto3, os, time
from datetime import datetime
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['FEED_SCORES_TABLE'])

# simple hourly buckets for context awareness
def get_time_bucket():
    hour = datetime.utcnow().hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 24:
        return "evening"
    else:
        return "night"

def listened(event, context):
    user_id = event["user_id"]
    genre = event["entity"]
    song = event['song']
    time_bucket = get_time_bucket()

    # Scoring heuristic:
    LISTEN_POINTS = 1          # baseline for listening
    RATING_BONUS = 1 if event.get("rated_positive") else 0
    TOTAL_POINTS = LISTEN_POINTS + RATING_BONUS

    # Current timestamp
    now = int(time.time())


    # DECAY SCORE. OLD ITEMS TEND TO BE DELETED IF DECAYED TO MUCH
    resp = table.query(
        KeyConditionExpression=Key("username").eq(user_id)
    )

    for item in resp.get("Items", []):
        sort_key = item["entity_type"]
        if not sort_key.startswith(f"genre#{time_bucket}"):
            continue  # only same time bucket
        if sort_key == f"genre#{time_bucket}":
            continue  # skip current genre

        old_score = item.get("score", 0)
        new_score = int(old_score * 0.9)

        if new_score < 1:
            table.delete_item(Key={"username": user_id, "entity_type": sort_key})
        else:
            table.update_item(
                Key={"user_id": user_id, "entity_type": sort_key},
                UpdateExpression="SET score = :s, last_updated=:u",
                ExpressionAttributeValues={":s": new_score, ":u": now}
            )

    return {
        "user_id": user_id,
        "entity_type" : "genre",
        "userListened" : True,
        "entity": genre,
        "song" : song,
        "points": TOTAL_POINTS,
        "time_bucket": time_bucket
    }
