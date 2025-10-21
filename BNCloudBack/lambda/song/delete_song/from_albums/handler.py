import boto3
import json

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')


def _discover_albums_with_song(song_id: str):
    found = []
    scan_kwargs = {}
    while True:
        resp = albums_table.scan(**scan_kwargs)
        for item in resp.get('Items', []):
            songs = item.get('songs', []) or []
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

    albums = _discover_albums_with_song(song_id)
    updated = 0

    for album in albums:
        album_id = (album or {}).get('id')
        if not album_id:
            continue
        try:
            album_item = albums_table.get_item(Key={'id': album_id}).get('Item')
            if not album_item:
                continue
            new_songs = [s for s in (album_item.get('songs') or []) if (s or {}).get('id') != song_id]
            if len(new_songs) != len(album_item.get('songs') or []):
                albums_table.update_item(
                    Key={'id': album_id},
                    UpdateExpression="SET songs = :s",
                    ExpressionAttributeValues={':s': new_songs}
                )
                updated += 1
        except Exception as e:
            print(f"Error removing song {song_id} from album {album_id}: {e}")

    return {"status": f"Song {song_id} removed from {updated} albums"}
