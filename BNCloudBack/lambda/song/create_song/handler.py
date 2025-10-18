import json
import uuid
import boto3
from datetime import datetime
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')
s3_bucket_name = 'songs-bucket-1'
s3_client = boto3.client('s3')

def create(event, context):
    data = json.loads(event['body'])

    # Generate a unique ID for the song
    song_id = str(uuid.uuid4())

    # Construct S3 keys for audio and image
    audio_key = f"{song_id}/audio/{data['audioFileName']}"
    image_key = f"{song_id}/image/{data['imageFileName']}"

    # DynamoDB item
    item = {
        'id': song_id,
        'name': data['name'],
        'genres': data.get('genres', []),
        'artists': data.get('artists', []),
        'audioKey': audio_key,
        'imageKey': image_key,
        'creationTime': data.get('creationTime', datetime.utcnow().isoformat()),
        'modificationTime': data.get('modificationTime', datetime.utcnow().isoformat()),
        'ratings': data.get('ratings', [])
    }

    # Save to DynamoDB
    songs_table.put_item(Item=item)

    audio_url = s3_client.generate_presigned_url(
    ClientMethod='put_object',
    Params={
        'Bucket': s3_bucket_name,
        'Key': audio_key
    },
    ExpiresIn=3600
)

    image_url = s3_client.generate_presigned_url(
    ClientMethod='put_object',
    Params={
        'Bucket': s3_bucket_name,
        'Key': image_key
    },
    ExpiresIn=3600
)

    response_body = {
        'songId': song_id,
        'audioUploadUrl': audio_url,
        'imageUploadUrl': image_url,
        's3Bucket': s3_bucket_name,
        'audioKey': audio_key,
        'imageKey': image_key
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_body),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }