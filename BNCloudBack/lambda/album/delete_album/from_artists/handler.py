import boto3
import json

dynamodb = boto3.resource('dynamodb')
artist_table = dynamodb.Table('Artists')

def delete(event, context):
    payload = event if isinstance(event, dict) else json.loads(event)
    album_id = payload.get('albumId')

    if not album_id:
        print("No albumId provided")
        return

    response = artist_table.scan()
    artists = response.get('Items', [])

    for artist in artists:
        albums = artist.get('Albums', [])
        new_albums = [a for a in albums if a.get('id') != album_id]
        if len(new_albums) != len(albums):
            artist_table.update_item(
                Key={'id': artist['id']},
                UpdateExpression="SET Albums = :albums",
                ExpressionAttributeValues={':albums': new_albums}
            )
            print(f"Removed album {album_id} from artist {artist['id']}")
