import json
import boto3

dynamodb = boto3.resource('dynamodb')
genres_table = dynamodb.Table('Genres')


def _discover_genres_with_artist(artist_id: str):
    found = []
    scan_kwargs = {}
    while True:
        resp = genres_table.scan(**scan_kwargs)
        for item in resp.get('Items', []):
            # Genres items use 'Artists' attribute (capital A)
            artists = item.get('Artists', []) or []
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

    genres = event.get('genres')
    if not genres:
        genres = _discover_genres_with_artist(artist_id)

    updated = 0
    for genre in genres:
        genre_id = (genre or {}).get('id')
        if not genre_id:
            continue

        try:
            genre_item = genres_table.get_item(Key={'id': genre_id}).get('Item')
            if not genre_item:
                continue

            # Work with 'Artists' attribute for genres
            current_artists = genre_item.get('Artists') or []
            new_artists = [a for a in current_artists if (a or {}).get('id') != artist_id]

            if len(new_artists) != len(current_artists):
                genres_table.update_item(
                    Key={'id': genre_id},
                    UpdateExpression="SET #A = :a",
                    ExpressionAttributeNames={'#A': 'Artists'},
                    ExpressionAttributeValues={':a': new_artists}
                )
                updated += 1
        except Exception as e:
            print(f"Error removing artist {artist_id} from genre {genre_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {updated} genres"}
