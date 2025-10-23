import json
import boto3
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response
from pre_authorize import pre_authorize
import os

table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

@pre_authorize(['Administrator','User'])
def discover(event, context):
    """
    Returns all distinct genres from DynamoDB where EntityType='genre'
    """
    genre_name = None
    if 'queryStringParameters' in event and event['queryStringParameters']:
        genre_name = event['queryStringParameters'].get('name')
    if genre_name:
        response = table.query(
            IndexName='EntityTypeIndex',
            KeyConditionExpression=Key('EntityType').eq('Genre') & Key('name').eq(genre_name)
        )
    
        items = response.get('Items', [])
        genres = [{
            'id': item['id'],
            'name': item['name'],
            'albums': item.get('Albums', []),  
            'artists': item.get('Artists', [])
        } for item in items]
        
        return create_response(200, genres)
    else:
        return create_response(400,{'message':'Genre name not found.'})