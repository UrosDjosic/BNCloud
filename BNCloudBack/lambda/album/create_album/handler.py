import json
import uuid
import boto3
from datetime import datetime
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')

def create(event, context):
    data = json.loads(event['body'])

    album_id = str(uuid.uuid4())

    item = {
        'id': album_id,
        'name': data['name'],
        'genres': data.get('genres', []),
        'artists': data.get('artists', []),
        'creationTime': data.get('creationTime', datetime.utcnow().isoformat()),
        'songs': data.get('songs', []),
    }

    songs_table.put_item(Item=item)

    return create_response(200, {"message": "Album created successfully", "albumId": album_id})