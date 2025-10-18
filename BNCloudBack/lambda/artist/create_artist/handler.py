import json
import os
import boto3
import uuid
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response

# Environment setup
table_name = os.environ['TABLE_NAME']  # Artist table
genre_table_name = os.environ['GENRE_TABLE_NAME']  # Genre table
dynamodb = boto3.resource('dynamodb')

def create(event, context):
    body = json.loads(event['body'])
    artist_id = str(uuid.uuid4())
    artist_name = body['name']
    biography = body['biography']
    genres_input = body.get('genres', [])

    artist_table = dynamodb.Table(table_name)
    genre_table = dynamodb.Table(genre_table_name)

    genres_full = []  # Will store [{id, name}, ...]

    for genre in genres_input:
        if isinstance(genre, dict):
            genre_name = genre.get('name')
            genre_id = genre.get('id')
        else:
            genre_name = str(genre)
            genre_id = None

        # Try finding genre by name if no id given
        if not genre_id:
            existing = genre_table.query(
                IndexName="EntityTypeIndex",
                KeyConditionExpression=Key('EntityType').eq('Genre') & Key('name').eq(genre_name)
            )

            if existing.get('Items'):
                genre_id = existing['Items'][0]['id']
            else:
                genre_id = str(uuid.uuid4())
                genre_table.put_item(
                    Item={
                        'id': genre_id,
                        'name': genre_name,
                        'EntityType': 'Genre',
                        'Artists': []
                    }
                )

        genre_table.update_item(
            Key={'id': genre_id},
            UpdateExpression="SET #A = list_append(if_not_exists(#A, :empty_list), :new_artist)",
            ConditionExpression="attribute_not_exists(#A) OR NOT contains(#A, :artist_check)",
            ExpressionAttributeNames={'#A': 'Artists'},
            ExpressionAttributeValues={
                ':new_artist': [{'id': artist_id, 'name': artist_name}],
                ':empty_list': [],
                ':artist_check': {'id': artist_id, 'name': artist_name}
            }
        )

        genres_full.append({'id': genre_id, 'name': genre_name})

    artist_table.put_item(
        Item={
            'id': artist_id,
            'name': artist_name,
            'biography': biography,
            'genres': genres_full,
            'EntityType': 'Artist'
        }
    )

    return create_response(200, {
        'message': f"Successfully created artist '{artist_name}'",
        'artist': {
            'id': artist_id,
            'name': artist_name,
            'biography': biography,
            'genres': genres_full
        }
    })
