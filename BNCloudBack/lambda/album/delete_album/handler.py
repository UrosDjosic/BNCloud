import os
import json
import boto3
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')
lambda_client = boto3.client('lambda')

def delete(event, context):
    try:
        album_id = event.get('pathParameters', {}).get('albumId')
        if not album_id:
            return create_response(400, {'message': 'albumId (from URL) is required'})

        # Get album info
        album = albums_table.get_item(Key={'id': album_id}).get('Item')
        if not album:
            return create_response(404, {'message': 'Album not found'})

        # cleanup lambdas asynchronly
        payload = {'albumId': album_id, 'album': album}

        for key in ['DELETE_ALBUM_FROM_ARTISTS', 'DELETE_ALBUM_FROM_GENRES', 'DELETE_ALBUM_FROM_SONGS']:
            target_lambda_arn = os.environ.get(key)
            if target_lambda_arn:
                lambda_client.invoke(
                    FunctionName=target_lambda_arn,
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                )

        # delete from Albums table
        albums_table.delete_item(Key={'id': album_id})

        return create_response(200, {'message': 'Album deleted successfully', 'albumId': album_id})

    except Exception as e:
        print(f"Error deleting album: {e}")
        return create_response(500, {'message': 'Internal server error', 'error': str(e)})
