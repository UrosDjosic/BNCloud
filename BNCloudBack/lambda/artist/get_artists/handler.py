import json
import os
import boto3
import uuid

# Import local utility module
from helpers.create_response import create_response

# Extract environment variable
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')


def get(event,context):
    table = dynamodb.Table(table_name)

    params = event.get('queryStringParameters', {}) or {}
    page_size = int(params.get('pageSize', 3))
    last_key_param = params.get('lastKey')

    last_key = None
    if last_key_param:
        last_key = {'id': last_key_param} 

    if last_key:
        response = table.scan(Limit=page_size, ExclusiveStartKey=last_key)
    else:
        response = table.scan(Limit=page_size)

    last_evaluated = response.get('LastEvaluatedKey')
    last_key_id = last_evaluated['id'] if last_evaluated else None

    return create_response(200, {
        'items': response.get('Items', []),
        'lastKey': last_key_id # send back for next page
    })