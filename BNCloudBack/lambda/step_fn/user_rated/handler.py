import json

def rated(event, context):
    """
    Handles 'user_rated_song' events.

    Expected event:
    {
        "event_type": "user_rated_song",
        "user_id": "123",
        "song": "{id,name,url}",
        "rating": 4   # int or float, typically 1–5
    }
    """

    user_id = event.get("user_id")
    song = event.get("song")
    rating = float(event.get("rating", 0))

    if not user_id or not song:
        raise ValueError("Missing user_id or song_id")

    #Defining heuristics
    RATING_POINTS = {
        5: 9,   
        4: 5,    
        3: 1,    
        2: -1,   
        1: -3    
    }

    points = RATING_POINTS.get(int(rating), 0)

    # Standardized payload for next Step Function stage
    payload = {
        "user_id": user_id,
        "entity_type": "song",
        "entity": song,
        "points": points,
        "userListened" : False
    }

    print(f"Processed rating event: {json.dumps(payload)}")

    return payload
