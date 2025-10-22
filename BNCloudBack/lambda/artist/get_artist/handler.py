import json
import boto3
import logging
from pre_authorize import pre_authorize


# Configure logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
artists_table = dynamodb.Table('Artists')

# Common CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
    'Access-Control-Allow-Headers': '*'
}

@pre_authorize(['Administrator','User'])
def get(event, context):
    try:
        # Ensure songId is provided
        path_params = event.get('pathParameters') or {}
        artist_id = path_params.get('artistId')

        if not artist_id:
            logger.warning("Missing artistId in path parameters.")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing artistId parameter'}),
                'headers': CORS_HEADERS
            }

        # Fetch song from DynamoDB
        response = artists_table.get_item(Key={'id': artist_id})
        artist = response.get('Item')

        if not artist:
            logger.info(f"Artist not found: {artist_id}")
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Artist not found'}),
                'headers': CORS_HEADERS
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(artist),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        logger.exception("Error fetching artist")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }
