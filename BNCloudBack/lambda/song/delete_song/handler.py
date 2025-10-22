import boto3
import json
import os
from helpers.invoke_lambda import invoke_target_async
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')


def delete(event, context):
    print("DeleteSongLambda triggered!")
    print("Event received:", json.dumps(event))
    path_params = event.get('pathParameters') or {}
    song_id = path_params.get('songId')

    if not song_id:
        return create_response(400, {"error": "songId is required"})

    # --- Load song data ---
    try:
        song_data = songs_table.get_item(Key={'id': song_id}).get('Item')
        if not song_data:
            return create_response(404, {"error": "Song not found"})
    except Exception as e:
        print("Error loading song:", e)
        return create_response(500, {"error": str(e)})

    # Prepare payloads for sub-handlers
    target_payloads = [
        (os.environ["DELETE_SONG_FROM_ARTISTS"], {"song_id": song_id}),
        (os.environ["DELETE_SONG_FROM_ALBUMS"], {"song_id": song_id}),
        (os.environ["DELETE_SONG_FROM_S3"], {
            "audioKey": song_data.get("audioKey"),
            "imageKey": song_data.get("imageKey"),
            "bucket": os.environ.get("SONGS_BUCKET_NAME", "songs-bucket-1")
        }),
    ]

    # Invoke other lambdas asynchronously
    for fn, payload in target_payloads:
        invoke_target_async(fn, payload)

    # Delete song item from Songs table
    try:
        songs_table.delete_item(Key={'id': song_id})
    except Exception as e:
        print("Error deleting song record:", e)
        return create_response(500, {"error": str(e)})

    return create_response(200, {"message": f"Song {song_id} deleted successfully"})
