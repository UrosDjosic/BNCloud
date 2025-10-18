import json
import uuid
import boto3
from datetime import datetime
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')

def create(event, context):
    data = json.loads(event['body'])

    album_id = str(uuid.uuid4())

    item = {
        'id': album_id,
        'name': data['name'],
        'genres': data.get('genres', []),
        'artists': data.get('artists', []),
        'songs': data.get('songs', []),
    }

    albums_table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({'albumId': album_id, 'message': 'Album created successfully'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }