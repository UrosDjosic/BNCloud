import json
import boto3

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')

def delete(event, context):
    artist_id = event.get('artist_id')
    songs = event.get('songs', [])

    if not artist_id or not songs:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing artist_id or songs"})}

    for song in songs:
        song_id = song.get('id')
        if not song_id:
            continue

        try:
            # Load song
            song_item = songs_table.get_item(Key={'id': song_id}).get('Item')
            if not song_item:
                continue

            # Filter OUT deleted artist
            new_artists = [a for a in song_item.get('artists', []) if a.get('id') != artist_id]

            # If changed update
            if len(new_artists) != len(song_item.get('artists', [])):
                songs_table.update_item(
                    Key={'id': song_id},
                    UpdateExpression="SET artists = :a",
                    ExpressionAttributeValues={':a': new_artists}
                )
        except Exception as e:
            print(f"Error removing artist {artist_id} from song {song_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {len(songs)} songs"}
