import json
import uuid
import boto3


dynamodb = boto3.resource('dynamodb')
userlist_table = dynamodb.Table('Userlists')

def create(event, context):
    data = json.loads(event['body'])

    # Generate a unique ID for the userlist
    userlist_id = str(uuid.uuid4())

    if not data.get('name') or not data.get('user') or not data.get('songs'):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required fields: name, user, songs'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }

    # DynamoDB item
    item = {
        'id': userlist_id,
        'name': data['name'],
        'user': data['user'],
        'songs': data.get('songs', [])
    }

    # Save to DynamoDB
    userlist_table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Userlist created successfully'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }