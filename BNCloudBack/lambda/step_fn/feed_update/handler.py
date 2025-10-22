import boto3, os, json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
FEED_SCORES_TABLE = os.environ['FEED_SCORES_TABLE']
USER_FEED_TABLE = os.environ['USER_FEED_TABLE']

scores_table = dynamodb.Table(FEED_SCORES_TABLE)
feed_table = dynamodb.Table(USER_FEED_TABLE)
RECORD_LIMIT = 7

def handler(event, context):
    """
    Expected input:
    {
      "user_id": "123"
    }
    """
    user_id = event["user_id"]

    # Group by entity_type
    songs, artists, genres = [], [], []
    song_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("song")).get("Items",[])
    artist_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("artist")).get("Items",[])
    genre_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("genre")).get("Items",[])

    songs = [item["entity"] for item in song_records][:RECORD_LIMIT]
    artists = [item["entity"] for item in artist_records][:RECORD_LIMIT]
    genres = [item["entity"] for item in genre_records][:RECORD_LIMIT]

    # Update UserFeed table
    feed_table.put_item(
        Item={
            "username": user_id,
            "songs": songs,
            "artists": artists,
            "genres": genres
        }
    )

    return {
        "ok": True,
        "user_id": user_id,
        "songs_count": len(songs),
        "artists_count": len(artists),
        "genres_count": len(genres)
    }
