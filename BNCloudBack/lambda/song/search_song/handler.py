import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from pre_authorize import pre_authorize

dynamodb = boto3.resource('dynamodb')
song_table = dynamodb.Table('Songs')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
    'Access-Control-Allow-Headers': '*'
}

def fix_decimals(obj):
    if isinstance(obj, list):
        return [fix_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: fix_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

@pre_authorize(['User'])
def search(event, context):
    try:
        path_params = event.get('pathParameters') or {}
        name = path_params.get('name')

        if not name:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing name parameter'}),
                'headers': CORS_HEADERS
            }

        name = name.replace('%20', ' ')

        response = song_table.scan(
            FilterExpression=Attr('name').eq(name)
        )
        found = fix_decimals(response.get('Items', []))

        return {
            'statusCode': 200,
            'body': json.dumps({'result': found}),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }
