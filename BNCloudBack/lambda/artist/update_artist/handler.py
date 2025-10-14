import json
import os
import boto3
import uuid

# Import local utility module
from helpers.create_response import create_response

table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')


def update(event,context):
    body = json.loads(event['body'])

    table = dynamodb.Table(table_name)
    # Update item
    response = table.update_item(
        Key={'id': body['id']},  # ID of the artist to update
        UpdateExpression="SET #n = :name, biography = :bio, genres = :genres",
        ExpressionAttributeNames={'#n': 'name'},  # because 'name' is a reserved word
        ExpressionAttributeValues={
            ':name': body['name'],
            ':bio': body['biography'],
            ':genres': body['genres']
        },
        ReturnValues="ALL_NEW"
    )
    # Create response
    body = response.get('Attributes', {})
    return create_response(200, body)