import json
import os
import boto3
import uuid
from boto3.dynamodb.conditions import Key
# Import local utility module
from helpers.create_response import create_response

# Extract environment variable
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')


def get(event, context):
    table = dynamodb.Table(table_name)
    params = event.get('queryStringParameters', {}) or {}
    page_size = int(params.get('pageSize', 100))
    last_key_param = params.get('lastKey')  # for pagination
    artist_id = params.get('artistId')      # filter by artist

    last_key = None
    if last_key_param:
        last_key = json.loads(last_key_param)

    if artist_id:
        response = table.query(
            KeyConditionExpression=Key('artist_id').eq(artist_id),
            Limit=page_size,
            ExclusiveStartKey=last_key
        )
    else:
        response = table.scan(
            Limit=page_size,
            ExclusiveStartKey=last_key
        )

    last_evaluated = response.get('LastEvaluatedKey')
    last_key_serialized = json.dumps(last_evaluated) if last_evaluated else None

    return create_response(200, {
        'items': response.get('Items', []),
        'lastKey': last_key_serialized
    })
