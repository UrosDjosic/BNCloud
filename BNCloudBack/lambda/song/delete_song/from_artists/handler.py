import boto3
import json

dynamodb = boto3.resource('dynamodb')
artists_table = dynamodb.Table('Artists')


def _discover_artists_with_song(song_id: str):
    found = []
    scan_kwargs = {}
    while True:
        resp = artists_table.scan(**scan_kwargs)
        for item in resp.get('Items', []):
            songs = item.get('Songs', []) or []
            if any((s or {}).get('id') == song_id for s in songs):
                found.append({'id': item.get('id')})
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        scan_kwargs['ExclusiveStartKey'] = lek
    return found


def delete(event, context):
    song_id = event.get('song_id')
    if not song_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing song_id"})}

    artists = _discover_artists_with_song(song_id)
    updated = 0

    for artist in artists:
        artist_id = (artist or {}).get('id')
        if not artist_id:
            continue
        try:
            artist_item = artists_table.get_item(Key={'id': artist_id}).get('Item')
            if not artist_item:
                continue
            new_songs = [s for s in (artist_item.get('Songs') or []) if (s or {}).get('id') != song_id]
            if len(new_songs) != len(artist_item.get('Songs') or []):
                artists_table.update_item(
                    Key={'id': artist_id},
                    UpdateExpression="SET Songs = :s",
                    ExpressionAttributeValues={':s': new_songs}
                )
                updated += 1
        except Exception as e:
            print(f"Error removing song {song_id} from artist {artist_id}: {e}")

    return {"status": f"Song {song_id} removed from {updated} artists"}
