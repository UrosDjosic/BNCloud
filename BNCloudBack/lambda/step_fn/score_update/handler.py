import boto3, json, os, time
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
FEED_SCORES_TABLE = os.environ['FEED_SCORES_TABLE']
table = dynamodb.Table(FEED_SCORES_TABLE)

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

def handler(event, context):
    """
    Expected input:
    {
      "user_id": "123",
      "entity_type": "song",
      "entity": some_object {id: .., name : ..., pictureUrl (song)},
      "points": 5
    }
    """
    user_id = event["user_id"]
    entity_type = event["entity_type"]    
    entity = event["entity"]        
    points = event.get("points", 1)      



    # timestamp (for recency)
    now = int(time.time())

    if entity_type == 'genre' and event['userListened'] == True:
        table.update_item(
            Key={"username": user_id, "entity_type": "song"},
            UpdateExpression="ADD score :p SET entity = :e, last_updated=:u",
            ExpressionAttributeValues={
                ":p": 1,
                ":e": event['song'],
                ":u": now
            }
        )
        time_bucket = get_time_bucket()
        entity_type = f"{event['entity']['name']}#{time_bucket}" 

    # Atomic add operation (creates record if it doesn't exist)
    table.update_item(
        Key={"username": user_id, "entity_type": entity_type},
        UpdateExpression="ADD score :p SET entity = :e, last_updated=:u",
        ExpressionAttributeValues={
            ":p": points,
            ":e": entity,
            ":u": now
        }
    )

    return {
        "ok": True,
        "user_id": user_id,
        "entity_type": entity_type,
        "entity": entity,
        "points_added": points
    }
