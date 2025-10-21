import boto3
import json

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')

def delete(event, context):
    payload = event if isinstance(event, dict) else json.loads(event)
    album_id = payload.get('albumId')

    response = songs_table.scan()
    songs = response.get('Items', [])

    for song in songs:
        if song.get('album', {}).get('id') == album_id:
            songs_table.update_item(
                Key={'id': song['id']},
                UpdateExpression="REMOVE album"
            )
            print(f"Removed album {album_id} reference from song {song['id']}")
