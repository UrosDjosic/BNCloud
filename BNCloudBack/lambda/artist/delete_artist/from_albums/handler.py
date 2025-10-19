import json
import boto3

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')

def delete(event, context):
    artist_id = event.get('artist_id')
    albums = event.get('albums', [])

    if not artist_id or not albums:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing artist_id or albums"})}

    for album in albums:
        album_id = album.get('id')
        if not album_id:
            continue

        try:
            album_item = albums_table.get_item(Key={'id': album_id}).get('Item')
            if not album_item:
                continue

            new_artists = [a for a in album_item.get('artists', []) if a.get('id') != artist_id]

            if len(new_artists) != len(album_item.get('artists', [])):
                albums_table.update_item(
                    Key={'id': album_id},
                    UpdateExpression="SET artists = :a",
                    ExpressionAttributeValues={':a': new_artists}
                )
        except Exception as e:
            print(f"Error removing artist {artist_id} from album {album_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {len(albums)} albums"}
