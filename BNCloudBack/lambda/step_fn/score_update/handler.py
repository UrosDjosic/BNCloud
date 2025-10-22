import boto3, json, os, time

dynamodb = boto3.resource('dynamodb')
FEED_SCORES_TABLE = os.environ['FEED_SCORES_TABLE']
table = dynamodb.Table(FEED_SCORES_TABLE)

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

    # Atomic add operation (creates record if it doesn't exist)
    table.update_item(
        Key={"user_id": user_id, "sort_key": entity_type},
        UpdateExpression="ADD score :p SET entity = :e, last_updated=:u",
        ExpressionAttributeValues={
            ":p": points,
            ":t": entity_type,
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
