import json
import boto3
import logging

# Configure logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')
s3_client = boto3.client('s3')

S3_BUCKET_NAME = 'songs-bucket-1'

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
        song_id = path_params.get('songId')

        if not song_id:
            logger.warning("Missing songId in path parameters.")
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing songId parameter'}),
                'headers': CORS_HEADERS
            }

        # Fetch song from DynamoDB
        response = songs_table.get_item(Key={'id': song_id})
        song = response.get('Item')

        if not song:
            logger.info(f"Song not found: {song_id}")
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Song not found'}),
                'headers': CORS_HEADERS
            }

        # Generate presigned URLs (only if keys exist)
        audio_url = None
        image_url = None

        if 'audioKey' in song:
            audio_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': song['audioKey']},
                ExpiresIn=3600
            )

        if 'imageKey' in song:
            image_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET_NAME, 'Key': song['imageKey']},
                ExpiresIn=3600
            )

        # Build response object
        response_body = {
            **song,
            'audioUrl': audio_url,
            'imageUrl': image_url
        }

        logger.info(f"Successfully retrieved song: {song_id}")

        return {
            'statusCode': 200,
            'body': json.dumps(response_body),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        logger.exception("Error fetching song")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }
