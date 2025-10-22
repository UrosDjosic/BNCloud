import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response
from pre_authorize import pre_authorize

import uuid

table_name = os.environ['TABLE_NAME']
genre_table_name = os.environ['GENRE_TABLE_NAME']  
dynamodb = boto3.resource('dynamodb')

@pre_authorize(['Administrator'])
def update(event, context):
    body = json.loads(event['body'])
    artist_id = body['id']
    new_name = body['name']
    new_bio = body['biography']
    new_genres_input = body.get('genres', [])

    artist_table = dynamodb.Table(table_name)
    genre_table = dynamodb.Table(genre_table_name)

    # ARtist
    existing_artist = artist_table.get_item(Key={'id': artist_id}).get('Item')
    if not existing_artist:
        return create_response(404, {'message': 'Artist not found'})

    old_genres = set(g['name'] for g in existing_artist.get('genres', []))

    # Parsing neew GENRES
    new_genres = []
    for genre in new_genres_input:
        if isinstance(genre, dict):
            genre_name = genre.get('name')
            genre_id = genre.get('id')
        else:
            genre_name = str(genre)
            genre_id = None
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

        new_genres.append({'id': genre_id, 'name': genre_name})

    new_genre_names = set(g['name'] for g in new_genres)

    # Changes update
    added_genres = new_genre_names - old_genres
    removed_genres = old_genres - new_genre_names

    # --- Add artist to new genres ---
    for genre in new_genres:
        if genre['name'] in added_genres:
            genre_table.update_item(
                Key={'id': genre['id']},
                UpdateExpression="SET #A = list_append(if_not_exists(#A, :empty_list), :new_artist)",
                ConditionExpression="attribute_not_exists(#A) OR NOT contains(#A, :artist_check)",
                ExpressionAttributeNames={'#A': 'Artists'},
                ExpressionAttributeValues={
                    ':new_artist': [{'id': artist_id, 'name': new_name}],
                    ':empty_list': [],
                    ':artist_check': {'id': artist_id, 'name': new_name}
                }
            )

    # Remove from deleted genres
    for genre_name in removed_genres:
        # Find exact genres record
        existing = genre_table.query(
            IndexName="EntityTypeIndex",
            KeyConditionExpression=Key('EntityType').eq('Genre') & Key('name').eq(genre_name)
        )
        if existing.get('Items'):
            genre_item = existing['Items'][0]
            genre_id = genre_item['id']
            artists = genre_item.get('Artists', [])
            updated_artists = [a for a in artists if a['id'] != artist_id]
            genre_table.update_item(
                Key={'id': genre_id},
                UpdateExpression="SET #A = :updated_list",
                ExpressionAttributeNames={'#A': 'Artists'},
                ExpressionAttributeValues={':updated_list': updated_artists}
            )

    # Updating artist
    artist_table.update_item(
        Key={'id': artist_id},
        UpdateExpression="SET #n = :name, biography = :bio, genres = :genres",
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':name': new_name,
            ':bio': new_bio,
            ':genres': new_genres
        }
    )

    return create_response(200, {
        'message': 'Artist updated successfully',
        'artist': {
            'id': artist_id,
            'name': new_name,
            'biography': new_bio,
            'genres': new_genres
        }
    })
