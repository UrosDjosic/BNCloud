import json
import boto3

dynamodb = boto3.resource('dynamodb')
genres_table = dynamodb.Table('Genres')

def delete(event, context):
    artist_id = event.get('artist_id')
    genres = event.get('genres', [])

    if not artist_id or not genres:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing artist_id or genres"})}

    for genre in genres:
        genre_id = genre.get('id')
        if not genre_id:
            continue

        try:
            genre_item = genres_table.get_item(Key={'id': genre_id}).get('Item')
            if not genre_item:
                continue

            new_artists = [a for a in genre_item.get('artists', []) if a.get('id') != artist_id]

            if len(new_artists) != len(genre_item.get('artists', [])):
                genres_table.update_item(
                    Key={'id': genre_id},
                    UpdateExpression="SET artists = :a",
                    ExpressionAttributeValues={':a': new_artists}
                )
        except Exception as e:
            print(f"Error removing artist {artist_id} from genre {genre_id}: {e}")

    return {"status": f"Artist {artist_id} removed from {len(genres)} genres"}
