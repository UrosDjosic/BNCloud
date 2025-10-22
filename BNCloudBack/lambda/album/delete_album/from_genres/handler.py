import boto3
import json

dynamodb = boto3.resource('dynamodb')
genre_table = dynamodb.Table('Genres')

def delete(event, context):
    payload = event if isinstance(event, dict) else json.loads(event)
    album_id = payload.get('albumId')

    response = genre_table.scan()
    genres = response.get('Items', [])

    for genre in genres:
        albums = genre.get('Albums', [])
        new_albums = [a for a in albums if a.get('id') != album_id]
        if len(new_albums) != len(albums):
            genre_table.update_item(
                Key={'id': genre['id']},
                UpdateExpression="SET Albums = :albums",
                ExpressionAttributeValues={':albums': new_albums}
            )
            print(f"Removed album {album_id} from genre {genre['id']}")
