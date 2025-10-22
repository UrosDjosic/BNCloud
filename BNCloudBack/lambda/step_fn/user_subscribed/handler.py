import json

def subscribed(event, context):
    """
    Handles both user_subscribed and user_unsubscribed events.

    Expected event input:
    {
        "event_type": "user_subscribed" | "user_unsubscribed",
        "user_id": "123",
        "subscription_type": "artist",
        "subscription_id": "abcd1234"
    }
    """
    user_id = event.get("user_id")
    sub_type = event.get("sub_type", "artist")
    entity = event.get("entity")
    event_type = event.get("event_type")
    POINTS = {
        "artist": 11,
        "genre": 8,
    }

    points = POINTS.get(sub_type, 5)

    # NEGATIVE ADJUSTMENT IF USER ACUTALLY UNSUBSCRIBED
    if event_type == "user_unsubscribed":
        points = -points

    payload = {
        "user_id": user_id,
        "entity_type": sub_type,
        "entity": entity,
        "points": points
    }

    print(f"Processed {event_type}: {json.dumps(payload)}")

    return payload
