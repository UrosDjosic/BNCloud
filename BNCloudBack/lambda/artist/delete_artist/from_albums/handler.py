import json
import boto3

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')


def _discover_albums_with_artist(artist_id: str):
    found = []
    scan_kwargs = {}
    while True:
        resp = albums_table.scan(**scan_kwargs)
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

    albums = event.get('albums')
    if not albums:
        albums = _discover_albums_with_artist(artist_id)

    updated = 0
    for album in albums:
        album_id = (album or {}).get('id')
        if not album_id:
            continue

        try:
            album_item = albums_table.get_item(Key={'id': album_id}).get('Item')
            if not album_item:
                continue

            new_artists = [a for a in (album_item.get('artists') or []) if (a or {}).get('id') != artist_id]

            if len(new_artists) != len(album_item.get('artists') or []):
                albums_table.update_item(
                    Key={'id': album_id},
                    UpdateExpression="SET artists = :a",
                    ExpressionAttributeValues={':a': new_artists}
                )
                updated += 1
        except Exception as e:
            print(f"Error removing artist {artist_id} from album {album_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {updated} albums"}
