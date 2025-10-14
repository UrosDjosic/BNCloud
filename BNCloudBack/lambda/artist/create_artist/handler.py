import json
import os
import boto3
import uuid
# Import local utility module
from helpers.create_response import create_response

# Extract environment variable
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def create(event, context):
    # Extract data from request
    body = json.loads(event['body'])
    
    # Get table instance connection
    table = dynamodb.Table(table_name)
    # Put item into table

    genres = body['genres']

    artist_id = str(uuid.uuid4())
    for genre in genres:
        response = table.put_item(
            Item={
                'id' : artist_id,
                'name': body['name'],
                'biography': body['biography'],
                'genre': genre
            }
        )
        # Create response
    body = {
        'message': 'Successfully created artist.'
    }
    return create_response(200, body)
