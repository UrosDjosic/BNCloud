import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')
songs_table = dynamodb.Table('Songs')
s3_client = boto3.client('s3')

S3_BUCKET_NAME = 'songs-bucket-1'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
    'Access-Control-Allow-Headers': '*'
}

def get(event, context):
    try:
        path_params = event.get('pathParameters') or {}
        album_id = path_params.get('albumId')

        if not album_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing albumId parameter'}),
                'headers': CORS_HEADERS
            }

        # Fetch album
        response = albums_table.get_item(Key={'id': album_id})
        album = response.get('Item')

        if not album:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Album not found'}),
                'headers': CORS_HEADERS
            }

        # Prepare songs array with minimal info
        songs_dto = []
        for s in album.get('songs', []):
            song_id = s.get('id')
            song_name = s.get('name')

            # Fetch song to get audioKey/imageKey for fileName
            song_resp = songs_table.get_item(Key={'id': song_id})
            song_item = song_resp.get('Item')
            file_name = None
            if song_item and 'audioKey' in song_item:
                file_name = song_item['audioKey'].split('/')[-1]

            songs_dto.append({
                'id': song_id,
                'name': song_name,
                'artists': s.get('artists', []),
                'fileName': file_name
            })

        album_dto = {
            'id': album['id'],
            'name': album['name'],
            'author': album.get('artists', [{}])[0] if album.get('artists') else {'id': '', 'name': ''},
            'songs': songs_dto,
            'genres': album.get('genres', [])
        }

        return {
            'statusCode': 200,
            'body': json.dumps(album_dto),
            'headers': CORS_HEADERS
        }

    except Exception as e:
        logger.exception("Error fetching album")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)}),
            'headers': CORS_HEADERS
        }