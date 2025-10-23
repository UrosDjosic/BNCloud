import boto3, os, json
from boto3.dynamodb.conditions import Key
from datetime import datetime
dynamodb = boto3.resource('dynamodb')
FEED_SCORES_TABLE = os.environ['FEED_SCORES_TABLE']
USER_FEED_TABLE = os.environ['USER_FEED_TABLE']

scores_table = dynamodb.Table(FEED_SCORES_TABLE)
feed_table = dynamodb.Table(USER_FEED_TABLE)
RECORD_LIMIT = 7
s3_client = boto3.client('s3')
S3_BUCKET_NAME = 'songs-bucket-1'

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
    
from boto3.dynamodb.conditions import Attr

def set_song_images(songs):
    for song in songs:
        image_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': song['imageKey']},
                ExpiresIn=3600
            )
        song['imageUrl'] = image_url
    return songs


def handler(event, context):
    """
    Expected input:
    {
      "user_id": "123"
    }
    """
    user_id = event["user_id"]

    time_bucket = get_time_bucket()
    # Group by entity_type
    songs, artists, genres = [], [], []

    #QUERYING SONGS  BY GSI username:entity_class so we can get all of entity_types user interacted with
    songs_resp = scores_table.query(
        IndexName="UserEntityClassIndex",
        KeyConditionExpression=Key("username").eq(user_id) & Key("entity_class").eq("song")
    )
    artists_resp = scores_table.query(
        IndexName="UserEntityClassIndex",
        KeyConditionExpression=Key("username").eq(user_id) & Key("entity_class").eq("artist")
    )
    genres_resp = scores_table.query(
        IndexName="UserEntityClassIndex",
        KeyConditionExpression=Key("username").eq(user_id) & Key("entity_class").eq("genre"),
        FilterExpression=(Attr("time_bucket").not_exists() | Attr("time_bucket").eq(""))
    )

    song_records = songs_resp.get("Items", [])
    artist_records = artists_resp.get("Items", [])
    genre_records = genres_resp.get("Items", [])

    # Time-bucketed genres
    genre_time_resp = scores_table.query(
        IndexName="UserEntityClassIndex",
        KeyConditionExpression=Key("username").eq(user_id) & Key("entity_class").eq("genre_time"),
        FilterExpression=Attr("time_bucket").eq(time_bucket)
    )
    genre_time_records = genre_time_resp.get("Items", [])
    print(f"Genre time records : {genre_time_records}, genre#{time_bucket}")
    print(f"Genre record {genre_records}")

    #sorting by score so we can search first three geenders!
    genre_records = sorted(genre_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]
    genre_time_records = sorted(genre_time_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]
    songs = [s["entity"] for s in sorted(song_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]]
    artists = [a["entity"] for a in sorted(artist_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]]


    songs = [item["entity"] for item in song_records][:RECORD_LIMIT]
    songs = set_song_images(songs)
    artists = [item["entity"] for item in artist_records][:RECORD_LIMIT]
    genre_favorite = [item["entity"] for item in genre_records][:RECORD_LIMIT]
    genre_time_favorites = [item["entity"] for item in genre_time_records][:RECORD_LIMIT]

    # Update UserFeed table
    feed_table.put_item(
        Item={
            "username": user_id,
            "songs": songs,
            "genre_favorite": genre_favorite,
            "genre_time_favorite" : genre_time_favorites,
            "artists": artists,
        }
    )

    return {
        "ok": True,
        "user_id": user_id,
        "songs_count": len(songs),
        "artists_count": len(artists),
        "genres_count": len(genres)
    }
