import boto3, json, os
from helpers.invoke_lambda import invoke_target_async
from helpers.create_response import create_response
from pre_authorize import pre_authorize



lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

@pre_authorize(['Administrator'])
def delete(event, context):
    path_params = event.get('pathParameters') or {}
    artist_id = path_params.get('artistId')

    if not artist_id:
        return create_response(400, {"error": "artist_id is required"})

    table_name = os.environ["TABLE_NAME"]
    table = dynamodb.Table(table_name)

    try:
        artist_data = table.get_item(Key={"id": artist_id}).get("Item")
        if not artist_data:
            return {"statusCode": 404, "body": json.dumps({"error": "Artist not found"})}

        print("Loaded artist:", artist_data)
    except Exception as e:
        print("Error loading artist:", e)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


    genres = artist_data.get("genres", [])
    albums = artist_data.get("Albums", [])
    songs = artist_data.get("Songs", [])

    target_payloads = [
        (os.environ["DELETE_ARTIST_FROM_SONGS"], {"artist_id": artist_id, "songs": songs}),
        (os.environ["DELETE_ARTIST_FROM_ALBUMS"], {"artist_id": artist_id, "albums": albums}),
        (os.environ["DELETE_ARTIST_FROM_GENRES"], {"artist_id": artist_id, "genres": genres}),
    ]
    for fn, payload in target_payloads:
        # Asynchronous invoke; do not block
        invoke_target_async(fn, payload)
    table.delete_item(Key={"id": artist_id})

    return create_response(200,{'message' : 'Deleted artist and references successfully!'})

