import json
import boto3
from helpers.create_response import create_response

dynamodb = boto3.resource('dynamodb')
albums_table = dynamodb.Table('Albums')
genre_table = dynamodb.Table('Genres')
artist_table = dynamodb.Table('Artists')

def update(event, context):
    """
    Update album name only.
    Expects JSON body: { "name": "New Album Name" }
    Album ID comes from path parameter: /album/{albumId}
    Also updates album name in Genres and Artists tables.
    """
    try:
        album_id = event.get('pathParameters', {}).get('albumId')
        data = json.loads(event.get('body') or '{}')
        new_name = data.get('name')

        if not album_id or not new_name:
            return create_response(400, {'message': 'albumId (from URL) and name are required'})

        #  Update album name in Albums table
        albums_table.update_item(
            Key={'id': album_id},
            UpdateExpression="SET #N = :new_name",
            ExpressionAttributeNames={'#N': 'name'},
            ExpressionAttributeValues={':new_name': new_name}
        )

        # Update album name inside all genres
        response = genre_table.scan()
        genres = response.get('Items', [])

        for genre in genres:
            albums_list = genre.get('Albums', [])
            updated = False

            for album in albums_list:
                if str(album.get('id')) == str(album_id):
                    album['name'] = new_name
                    updated = True

            if updated:
                print(f"Updating genre {genre['id']} -> {albums_list}")
                genre_table.update_item(
                    Key={'id': genre['id']},
                    UpdateExpression="SET Albums = :albums",
                    ExpressionAttributeValues={':albums': albums_list}
                )

        # Update album name inside all artists
        response = artist_table.scan()
        artists = response.get('Items', [])

        for artist in artists:
            albums_list = artist.get('Albums', [])
            updated = False

            for album in albums_list:
                if str(album.get('id')) == str(album_id):
                    album['name'] = new_name
                    updated = True

            if updated:
                print(f"Updating artist {artist['id']} -> {albums_list}")
                artist_table.update_item(
                    Key={'id': artist['id']},
                    UpdateExpression="SET Albums = :albums",
                    ExpressionAttributeValues={':albums': albums_list}
                )

        return create_response(200, {'albumId': album_id, 'message': 'Album name updated successfully'})

    except Exception as e:
        print(f"Error updating album: {str(e)}")
        return create_response(500, {'message': 'Internal server error', 'error': str(e)})