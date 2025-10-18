import json
import boto3
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response
import os
table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def get(event, context):
    """
    Returns all distinct genres from DynamoDB where EntityType='genre'
    """
    response = table.query(
        IndexName='EntityTypeIndex',  # your GSI name
        KeyConditionExpression=Key('EntityType').eq('Genre')
    )
    
    items = response.get('Items', [])
    genres = [{'id': item['id'], 'name': item['name']} for item in items]
    
    return create_response(200, {'genres': genres})