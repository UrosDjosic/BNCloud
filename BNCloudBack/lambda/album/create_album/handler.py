import json
import uuid
import boto3
from helpers.create_response import create_response
from pre_authorize import pre_authorize

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')
genre_table = dynamodb.Table('Genres')
artist_table = dynamodb.Table('Artists')

@pre_authorize(['Administrator'])
def create(event, context):
    data = json.loads(event['body'])
    album_id = str(uuid.uuid4())

    genres_input = data.get('genres', [])
    genres_input = list({g['id']: g for g in genres_input}.values())

    genres_full = []

    for genre in genres_input:
        genre_id = genre.get('id')
        genre_name = genre.get('name')
        if not genre_id or not genre_name:
            continue

        genre_table.update_item(
            Key={'id': genre_id},
            UpdateExpression="SET Albums = list_append(if_not_exists(Albums, :empty_list), :new_album)",
            ExpressionAttributeValues={
                ':new_album': [{'id': album_id, 'name': data['name']}],
                ':empty_list': []
            }
        )

        genres_full.append({'id': genre_id, 'name': genre_name})

    for artist in data.get('artists', []):
        artist_id = artist.get('id')
        if not artist_id:
            continue

        try:
            artist_table.update_item(
                Key={'id': artist_id},
                UpdateExpression="SET Albums = list_append(if_not_exists(Albums, :empty_list), :new_album)",
                ExpressionAttributeValues={
                    ':new_album': [{'id': album_id, 'name': data['name']}],
                    ':empty_list': []
                }
            )
        except Exception as e:
            print(f"Failed to update artist {artist_id}: {str(e)}")

    item = {
        'id': album_id,
        'name': data['name'],
        'genres': genres_full,
        'artists': data.get('artists', []),
        'songs': data.get('songs', []),
    }

    albums_table.put_item(Item=item)

    return create_response(200, {'albumId': album_id, 'message': 'Album created successfully'})
