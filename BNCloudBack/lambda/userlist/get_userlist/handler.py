import json
import boto3

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
userlist_table = dynamodb.Table('Userlists')

# Common CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
    'Access-Control-Allow-Headers': '*'
}

def get(event, context):
    try:
        # Ensure songId is provided
        path_params = event.get('pathParameters') or {}
        userlist_id = path_params.get('userlistId')

        if not userlist_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing userlistId parameter'}),
                'headers': CORS_HEADERS
            }

        # Fetch song from DynamoDB
        response = userlist_table.get_item(Key={'id': userlist_id})
        userlist = response.get('Item')

        if not userlist:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Song not found'}),
                'headers': CORS_HEADERS
            }

        return {
            'statusCode': 200,
            'body': json.dumps(userlist),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }
