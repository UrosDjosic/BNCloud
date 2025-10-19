import json
import uuid
import boto3
from datetime import datetime
from helpers.create_response import create_response
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')
genre_table = dynamodb.Table('Genres')

def create(event, context):
    data = json.loads(event['body'])

    album_id = str(uuid.uuid4())

    genres_input = data.get('genres', [])
    genres_input = list({g['id']: g for g in genres_input}.values())

    genres_full = []

    for genre in genres_input:
        if isinstance(genre, dict):
            genre_name = genre.get('name')
            genre_id = genre.get('id')
        else:
            genre_name = str(genre)
            genre_id = None

        if not genre_name or not genre_id:
            continue  # skip empty genres or missing IDs

        # Add album to genre's Albums list
        genre_table.update_item(
            Key={'id': genre_id},
            UpdateExpression="SET #A = list_append(if_not_exists(#A, :empty_list), :new_album)",
            ConditionExpression="attribute_not_exists(#A) OR NOT contains(#A_ids, :album_id)",
            ExpressionAttributeNames={'#A': 'Albums', '#A_ids': 'AlbumIds'},
            ExpressionAttributeValues={
                ':new_album': [{'id': album_id, 'name': data['name']}],
                ':empty_list': [],
                ':album_id': album_id
            }
        )

        genres_full.append({'id': genre_id, 'name': genre_name})
    item = {
        'id': album_id,
        'name': data['name'],
        'genres': genres_full,
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