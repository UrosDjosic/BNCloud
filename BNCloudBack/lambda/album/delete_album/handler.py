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

        # async cleanup (artists, genres)
        payload = {'albumId': album_id, 'album': album}
        for key in ['DELETE_ALBUM_FROM_ARTISTS', 'DELETE_ALBUM_FROM_GENRES']:
            target_lambda_arn = os.environ.get(key)
            if target_lambda_arn:
                lambda_client.invoke(
                    FunctionName=target_lambda_arn,
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                )

        #  delete all songs in this album
        delete_song_lambda_arn = os.environ.get('DELETE_SONG')
        if delete_song_lambda_arn:
            for song in album.get('songs', []):
                song_id = song.get('id')
                if song_id:
                    print(f"DEBUG: Invoking delete_song_lambda for song_id={song_id} using {delete_song_lambda_arn}")

                    response = lambda_client.invoke(
                        FunctionName=delete_song_lambda_arn,
                        InvocationType='RequestResponse',
                        Payload=json.dumps({
                            "pathParameters": {"songId": song_id}  
                        })
                    )

                    payload = response["Payload"].read().decode()
                    print(f"DEBUG: delete_song_lambda response for {song_id}: {payload}")

                    print(f"Triggered deletion of song {song_id} from album {album_id}")

        # finally delete album itself
        albums_table.delete_item(Key={'id': album_id})

        print(f"DEBUG: DELETE_SONG env = {os.environ.get('DELETE_SONG')}")

        return create_response(200, {'message': 'Album deleted successfully', 'albumId': album_id})

    except Exception as e:
        print(f"Error deleting album: {e}")
        return create_response(500, {'message': 'Internal server error', 'error': str(e)})
