import json
import uuid
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
import os
from pre_authorize import pre_authorize


dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')
s3_bucket_name = 'songs-bucket-1'
s3_client = boto3.client('s3')

@pre_authorize(['Administrator'])
def update_image(event, context):
    data = json.loads(event['body'])
    song_id = data.get('songId')
    image_filename = data.get('image')
    if not song_id or not image_filename:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'songId and image are required'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    item = songs_table.get_item(Key={'id': song_id})
    if not item.get('Item'):
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Song not found'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }
    
    old_image_key = item['Item'].get('imageKey')
    new_image_key = f"{song_id}/image/{image_filename}"

    delete_old_url = s3_client.generate_presigned_url(
        ClientMethod='delete_object',
        Params={
            'Bucket': s3_bucket_name,
            'Key': old_image_key
        },
        ExpiresIn=3600
    )
    upload_new_url = s3_client.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': s3_bucket_name,
            'Key': new_image_key
        },
        ExpiresIn=3600
    )

    modification_time = datetime.utcnow().isoformat()
    songs_table.update_item(
        Key={'id': song_id},
        UpdateExpression='SET imageKey = :new_key, modificationTime = :mod_time',
        ExpressionAttributeValues={
            ':new_key': new_image_key,
            ':mod_time': modification_time
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'deleteOldUrl': delete_old_url,
            'uploadNewUrl': upload_new_url
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Access-Control-Allow-Headers': '*'
        }
    }