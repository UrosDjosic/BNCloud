import json
import uuid
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
import os


dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')

def rate(event, context):
    data = json.loads(event['body'])
    song_id = data.get('song')
    rating = data.get('stars')
    user_sub = data.get('user')
    if not song_id or not user_sub or rating is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'song, user, and rating are ALL required'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    item = songs_table.get_item(Key={'id': song_id})
    if not item.get('Item'):
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Song not found'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    ratings = item['Item'].get('ratings', [])
    # Check if user already rated
    updated = False
    for r in ratings:
        if r.get('user') == user_sub:
            r['stars'] = rating
            updated = True
            break

    if not updated:
        ratings.append({'user': user_sub, 'stars': rating})

    # Save back to DynamoDB
    songs_table.update_item(
        Key={'id': song_id},
        UpdateExpression='SET ratings = :r, modificationTime = :m',
        ExpressionAttributeValues={
            ':r': ratings,
            ':m': datetime.utcnow().isoformat()
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Ratings updated successfully'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }