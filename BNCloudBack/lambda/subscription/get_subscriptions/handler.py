import os
import boto3
from boto3.dynamodb.conditions import Key
from helpers.create_response import create_response

dynamodb = boto3.resource("dynamodb")

table_name = os.environ.get('TABLE_NAME','Subscriptions')

def get(event,context):
    path_params = event.get('pathParameters') or {}
    user_email = path_params.get('userEmail')
    print(f"path params: {path_params}")
    print(f"user_email extracted: {user_email}")
    
    table = dynamodb.Table(table_name)

    subscriptions = table.query(
        IndexName='user_email-index',
        KeyConditionExpression=Key('user_email').eq(user_email))


    return create_response(200, subscriptions.get("Items",[]))

