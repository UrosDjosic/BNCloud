import json
import uuid
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
import os


dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
songs_table = dynamodb.Table('Songs')
genre_table = dynamodb.Table('Genres')
artists_table = dynamodb.Table('Artists')
s3_bucket_name = 'songs-bucket-1'
s3_client = boto3.client('s3')

def create(event, context):
    data = json.loads(event['body'])

    # Generate a unique ID for the song
    song_id = str(uuid.uuid4())

    # Construct S3 keys for audio and image
    audio_key = f"{song_id}/audio/{data['audioFileName']}"
    image_key = f"{song_id}/image/{data['imageFileName']}"

    genres_input = data.get('genres', [])
    genres_full = []

    for genre in genres_input:
        if isinstance(genre, dict):
            genre_name = genre.get('name')
            genre_id = genre.get('id')
        else:
            genre_name = str(genre)
            genre_id = None

        if not genre_name:
            continue  # skip empty genre names

        # Check if genre exists
        if not genre_id:
            existing = genre_table.query(
                IndexName="EntityTypeIndex",
                KeyConditionExpression=Key('EntityType').eq('Genre') & Key('name').eq(genre_name)
            )
            if existing.get('Items'):
                genre_id = existing['Items'][0]['id']
            else:
                # Create new genre in table
                genre_id = str(uuid.uuid4())
                genre_table.put_item(
                    Item={
                        'id': genre_id,
                        'name': genre_name,
                        'EntityType': 'Genre'
                    }
                )

        genres_full.append({'id': genre_id, 'name': genre_name})

    # DynamoDB item
    item = {
        'id': song_id,
        'name': data['name'],
        'genres': genres_full,
        'artists': data.get('artists', []),
        'audioKey': audio_key,
        'imageKey': image_key,
        'creationTime': data.get('creationTime', datetime.utcnow().isoformat()),
        'modificationTime': data.get('modificationTime', datetime.utcnow().isoformat()),
        'ratings': data.get('ratings', [])
    }

    for artist in data.get('artists', []):
        artist_id = artist.get('id')
        artist_name = artist.get('name')

        if not artist_id:
            continue 

        # Update artist record to add the new song to its "Songs" attribute
        #ADDING SONG TO ARTIST!!
        artists_table.update_item(
            Key={'id': artist_id},
            UpdateExpression="SET Songs = list_append(if_not_exists(Songs, :empty_list), :new_song)",
            ExpressionAttributeValues={
                ':new_song': [{'id': song_id, 'name': data['name']}],
                ':empty_list': []
            }
        )

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

    '''''sqs.send_message(
        QueueUrl=os.environ['QUEUE_URL'],
        MessageBody=json.dumps({
            "event_type": "new_song",
            "song": {
                'name': data['name'],
                'genres': genres_full,
                'artists': data.get('artists', []),
            },
        })
    )'''''

    return {
        'statusCode': 200,
        'body': json.dumps(response_body),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }