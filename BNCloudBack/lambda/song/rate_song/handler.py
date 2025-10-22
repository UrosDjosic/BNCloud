import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from pre_authorize import pre_authorize
from decimal import Decimal
import os

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client("sqs")
songs_table = dynamodb.Table('Songs')
ratings_table = dynamodb.Table('Ratings')


@pre_authorize(['User'])
def rate(event, context):
    data = json.loads(event['body'])
    song_id = data.get('song')
    rating = data.get('stars')
    user_sub = data.get('user')

    if not song_id or not user_sub or rating is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'song, user, and rating are ALL required'}),
            'headers': _cors_headers()
        }

    # Song GET
    song_item = songs_table.get_item(Key={'id': song_id})
    if 'Item' not in song_item:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Song not found'}),
            'headers': _cors_headers()
        }

    # If already rated!
    existing = ratings_table.get_item(Key={'user': user_sub, 'song_id': song_id})
    now = datetime.utcnow().isoformat()

    #sending this to sqs
    final_rating = 0

    if 'Item' in existing:
        old_rating = int(existing['Item']['stars'])
        diff = int(rating) - old_rating

        final_rating = diff

        # Update user's rating
        ratings_table.update_item(
            Key={'user': user_sub, 'song_id': song_id},
            UpdateExpression='SET stars = :r',
            ExpressionAttributeValues={':r': int(rating)}
        )

        # Get current song stats
        current_song = song_item['Item']
        sum_ratings = current_song.get('sumRatings', 0) + diff
        num_ratings = current_song.get('numRatings', 1)
        avg_rating = sum_ratings / num_ratings

        # Update totals
        songs_table.update_item(
            Key={'id': song_id},
            UpdateExpression='SET sumRatings = :s, avgRating = :a',
            ExpressionAttributeValues={
                ':s': Decimal(sum_ratings),
                ':a': Decimal(avg_rating),
            }
        )
        message = 'Rating updated successfully'

    else:
        final_rating = rating
        # New rating — increment count, add to sum, recalc average
        ratings_table.put_item(
            Item={
                'user': user_sub,
                'song_id': song_id,
                'stars': int(rating),
            }
        )

        current_song = song_item['Item']
        sum_ratings = current_song.get('sumRatings', 0) + int(rating)
        num_ratings = current_song.get('numRatings', 0) + 1
        avg_rating = sum_ratings / num_ratings

        songs_table.update_item(
            Key={'id': song_id},
            UpdateExpression='SET sumRatings = :s, numRatings = :n, avgRating = :a',
            ExpressionAttributeValues={
                ':s': Decimal(sum_ratings),
                ':n': Decimal(num_ratings),
                ':a': Decimal(sum_ratings / num_ratings),
            }
        )
        message = 'Rating added successfully'

        sqs.send_message(
            QueueUrl=os.environ["FEED_QUEUE_URL"],
            MessageBody=json.dumps({
                "event_type": "user_rated_song",
                "user_id": event["userId"],
                "song": {
                    "id": song_id,
                    "name": song_item['Item']["name"],
                    "imageKey" : song_item['Item']["imageKey"]
                },
                "rating" : rating
            })
        )


    return {
        'statusCode': 200,
        'body': json.dumps({'message': message}),
        'headers': _cors_headers()
    }


def _cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
        'Access-Control-Allow-Headers': '*'
    }
