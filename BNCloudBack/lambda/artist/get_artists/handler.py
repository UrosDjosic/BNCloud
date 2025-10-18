import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response

# Environment variable for table name
TABLE_NAME = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')


def get(event, context):
    try:
        table = dynamodb.Table(TABLE_NAME)
        params = event.get('queryStringParameters') or {}

        # Pagination
        page_size = int(params.get('pageSize', 100))
        last_key_param = params.get('lastKey')
        last_key = None
        if last_key_param:
            try:
                last_key = json.loads(last_key_param)
                if not isinstance(last_key, dict):
                    last_key = None
            except json.JSONDecodeError:
                last_key = None

        # Optional filter by artist_id
        artist_id = params.get('artistId')

        if artist_id:
            query_kwargs = {
                'KeyConditionExpression': Key('artist_id').eq(artist_id),
                'Limit': page_size
            }
            if last_key:
                query_kwargs['ExclusiveStartKey'] = last_key

            response = table.query(**query_kwargs)
        else:
            scan_kwargs = {'Limit': page_size}
            if last_key:
                scan_kwargs['ExclusiveStartKey'] = last_key

            response = table.scan(**scan_kwargs)

        last_evaluated = response.get('LastEvaluatedKey')
        last_key_serialized = json.dumps(last_evaluated) if last_evaluated else None

        return create_response(200, {
            'items': response.get('Items', []),
            'lastKey': last_key_serialized
        })

    except Exception as e:
        return create_response(500, {'message': str(e)})
