import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('Songs')
artists_table = dynamodb.Table('Artists')
genres_table = dynamodb.Table('Genres')
albums_table = dynamodb.Table('Albums')


def update(event, context):
    try:
        data = json.loads(event['body'])
        song_id = data.get('songId')
        if not song_id:
            return {'statusCode': 400, 'body': json.dumps({'message': 'songId is required'})}

        # --- Učitaj postojeću pesmu ---
        existing_song = songs_table.get_item(Key={'id': song_id}).get('Item')
        if not existing_song:
            return {'statusCode': 404, 'body': json.dumps({'message': 'Song not found'})}

        new_name = data.get('name', existing_song['name'])
        new_artists = data.get('artists', existing_song.get('artists', []))
        new_genres = data.get('genres', existing_song.get('genres', []))
        modification_time = datetime.utcnow().isoformat()

        # --- Ažuriraj Songs tabelu ---
        songs_table.update_item(
            Key={'id': song_id},
            UpdateExpression="SET #N = :name, artists = :artists, genres = :genres, modificationTime = :modTime",
            ExpressionAttributeValues={
                ':name': new_name,
                ':artists': new_artists,
                ':genres': new_genres,
                ':modTime': modification_time
            },
            ExpressionAttributeNames={'#N': 'name'}
        )

        # --- Ažuriraj Artiste ---
        old_artist_ids = {a['id'] for a in existing_song.get('artists', []) if a.get('id')}
        new_artist_ids = {a['id'] for a in new_artists if a.get('id')}

        # Ukloni pesmu iz starih artista koji više nisu povezani
        for artist_id in old_artist_ids - new_artist_ids:
            artist_item = artists_table.get_item(Key={'id': artist_id}).get('Item')
            if artist_item and 'Songs' in artist_item:
                updated_songs = [s for s in artist_item['Songs'] if s['id'] != song_id]
                artists_table.update_item(
                    Key={'id': artist_id},
                    UpdateExpression="SET Songs = :songs",
                    ExpressionAttributeValues={':songs': updated_songs}
                )

        # Dodaj pesmu novim artistima (kao u create_song)
        for artist in new_artists:
            artist_id = artist.get('id')
            artist_name = artist.get('name')
            if not artist_id:
                continue

            artists_table.update_item(
                Key={'id': artist_id},
                UpdateExpression="SET Songs = list_append(if_not_exists(Songs, :empty_list), :new_song)",
                ExpressionAttributeValues={
                    ':new_song': [{'id': song_id, 'name': new_name}],
                    ':empty_list': []
                }
            )

        # --- Ažuriraj Album ako sadrži pesmu ---
        response = albums_table.scan()
        for album in response.get('Items', []):
            songs_in_album = album.get('songs', [])
            updated = False
            for s in songs_in_album:
                if s.get('id') == song_id:
                    s['name'] = new_name
                    updated = True

            if updated:
                albums_table.update_item(
                    Key={'id': album['id']},
                    UpdateExpression="SET songs = :songs",
                    ExpressionAttributeValues={':songs': songs_in_album}
                )

        return {
            'statusCode': 200,
            'body': json.dumps({'songId': song_id, 'message': 'Song updated successfully'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': '*'
            }
        }

    except Exception as e:
        print(f"Error updating song: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }