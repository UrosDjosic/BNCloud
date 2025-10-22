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

def get_genre_songs(genre_records, genre_time_records):
    """
    For each top genre (including time-bucketed ones),
    find the first song in Songs table that contains that genre in its 'genres' list.
    """
    table = dynamodb.Table("Songs")

    # Pick top 3 from each list
    top_genres = [g["entity"] for g in genre_records[:3]]
    top_genres_time = [g["entity"] for g in genre_time_records[:3]]

    print(f"{top_genres} TOP GENRES")
    print(f"{top_genres_time} TOP GENRES TIME")

    # Deduplicate but preserve order
    unique_genres = []
    for g in top_genres + top_genres_time:
        if g not in unique_genres:
            unique_genres.append(g)

    print(f"Unique genres {unique_genres}")
    found_songs = []


    for genre in unique_genres:
        resp = table.scan(
            FilterExpression=Attr("genres").contains(genre),
            Limit=1
        )
    

        items = resp.get("Items", [])
        print(f"{items} ITEM")
        if items:
            item = items[0]
            song = {
                'id' : item['id'],
                'name' : item['name'],
            }
            found_songs.append(song)

    return set_song_images(found_songs)

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
    song_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("song")).get("Items",[])
    artist_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("artist")).get("Items",[])
    genre_records = scores_table.query(KeyConditionExpression=Key("username").eq(user_id) & Key("entity_type").eq("genre")).get("Items",[])
    genre_time_records = scores_table.query(
            KeyConditionExpression=Key("username").eq(user_id),
            FilterExpression=Attr("entity_type").contains(f"#{time_bucket}")
    ).get("Items",[])
    print(f"Genre time records : {genre_time_records}, genre#{time_bucket}")
    print(f"Genre record {genre_records}")

    #sorting by score so we can search first three geenders!
    genre_records.sort(key=lambda x: x.get("score", 0), reverse=True)
    genre_time_records.sort(key=lambda x: x.get("score", 0), reverse=True)
    songs = [s["entity"] for s in sorted(song_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]]
    artists = [a["entity"] for a in sorted(artist_records, key=lambda x: x.get("score", 0), reverse=True)[:RECORD_LIMIT]]


    songs = [item["entity"] for item in song_records][:RECORD_LIMIT]
    songs = set_song_images(songs)
    artists = [item["entity"] for item in artist_records][:RECORD_LIMIT]
    genre_songs = get_genre_songs(genre_records=genre_records,genre_time_records=genre_time_records)
    print(f"GENRE SONGS : {genre_songs}")

    # Update UserFeed table
    feed_table.put_item(
        Item={
            "username": user_id,
            "songs": songs,
            "genre_songs": genre_songs,
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
