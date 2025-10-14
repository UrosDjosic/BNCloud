import json
import os
import boto3
from helpers.create_response import create_response

table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
from boto3.dynamodb.conditions import Key

def update(event, context):
    body = json.loads(event['body'])
    artist_id = body['artist_id']          # PK
    new_name = body['name']
    new_bio = body['biography']
    new_genres = set(body['genres'])       # list of new genres

    table = dynamodb.Table(table_name)

    #Querying
    response = table.query(
        KeyConditionExpression=Key('artist_id').eq(artist_id)
    )
    items = response['Items']
    existing_genres = set(item['genre'] for item in items)

    # Deletin items which genres does not exist anymore
    for item in items:
        if item['genre'] not in new_genres:
            table.delete_item(
                Key={'artist_id': artist_id, 'genre': item['genre']}
            )

    # Update existing!
    for item in items:
        if item['genre'] in new_genres:
            table.update_item(
                Key={'artist_id': artist_id, 'genre': item['genre']},
                UpdateExpression="SET #n = :name, biography = :bio",
                ExpressionAttributeNames={'#n': 'name'},
                ExpressionAttributeValues={
                    ':name': new_name,
                    ':bio': new_bio
                }
            )

    # New genres
    for genre in new_genres - existing_genres:
        table.put_item(
            Item={
                'artist_id': artist_id,
                'genre': genre,
                'name': new_name,
                'biography': new_bio
            }
        )

    return create_response(200, {"message": "Artist updated successfully"})
