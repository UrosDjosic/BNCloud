import os
import json
import boto3

sns = boto3.client('sns')

def notify(event, context):
    for record in event['Records']:
        msg = json.loads(record['body'])
        song = msg.get('song', {})
        song_name = song.get('name')
        artists = song.get('artists', [])
        genres = song.get('genres', [])

        for artist in artists:
            artist_id = artist.get('id') if isinstance(artist, dict) else artist
            topic_name = f"artist_{artist_id}"
            topic_arn = f"arn:aws:sns:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:{topic_name}"

            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Subject=f"New song from {artist.get('name', artist_id)}!",
                    Message=f"A new song '{song_name}' was released by {artist.get('name', artist_id)}."
                )
                print(f"Published notification for {artist_id}")
            except Exception as e:
                print(f"Failed to notify for {artist_id}: {e}")

        for genre in genres:
            genre_id = genre.get('id') if isinstance(genre, dict) else genre
            topic_name = f"genre_{genre_id}"
            topic_arn = f"arn:aws:sns:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:{topic_name}"

            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Subject=f"New {genre.get('name',genre_id)} song released!",
                    Message=f"A new {genre.get('name',genre_id)} song '{song_name}' was released."
                )
                print(f"Published notification for genre {genre}")
            except Exception as e:
                print(f"Failed to notify for genre {genre}: {e}")
