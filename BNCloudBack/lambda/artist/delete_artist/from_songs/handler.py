import json
import boto3

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')


def _discover_songs_with_artist(artist_id: str):
    found = []
    scan_kwargs = {}
    while True:
        resp = songs_table.scan(**scan_kwargs)
        for item in resp.get('Items', []):
            artists = item.get('artists', []) or []
            if any((a or {}).get('id') == artist_id for a in artists):
                found.append({'id': item.get('id')})
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        scan_kwargs['ExclusiveStartKey'] = lek
    return found


def delete(event, context):
    artist_id = event.get('artist_id')
    if not artist_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing artist_id"})}

    songs = event.get('songs')
    if not songs:
        # Discover songs that reference the artist if none provided
        songs = _discover_songs_with_artist(artist_id)

    updated = 0
    for song in songs:
        song_id = (song or {}).get('id')
        if not song_id:
            continue

        try:
            song_item = songs_table.get_item(Key={'id': song_id}).get('Item')
            if not song_item:
                continue

            new_artists = [a for a in (song_item.get('artists') or []) if (a or {}).get('id') != artist_id]

            if len(new_artists) != len(song_item.get('artists') or []):
                songs_table.update_item(
                    Key={'id': song_id},
                    UpdateExpression="SET artists = :a",
                    ExpressionAttributeValues={':a': new_artists}
                )
                updated += 1
        except Exception as e:
            print(f"Error removing artist {artist_id} from song {song_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {updated} songs"}
