import json
import boto3
from boto3.dynamodb.conditions import Attr
from pre_authorize import pre_authorize

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
userlist_table = dynamodb.Table('Userlists')

# Common CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
    'Access-Control-Allow-Headers': '*'
}

@pre_authorize(['User'])
def get(event, context):
    try:
        path_params = event.get('pathParameters') or {}
        user_id = path_params.get('userId')

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing user_Id parameter'}),
                'headers': CORS_HEADERS
            }
        
        found = []

        response = userlist_table.scan(
            FilterExpression=Attr('user').eq(user_id)
        )
        found = response.get('Items', [])

        return {
            'statusCode': 200,
            'body': json.dumps({'usersLists': found}),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }
