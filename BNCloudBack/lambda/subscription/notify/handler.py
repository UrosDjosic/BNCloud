import os
import json
import boto3

sns = boto3.client('sns')

def handler(event, context):
    for record in event['Records']:
        msg = json.loads(record['body'])
        song = msg.get('song', {})
        song_name = song.get('name')
        artists = song.get('artists', [])
        genres = song.get('genres', [])

        for artist_id in artists:
            topic_name = f"artist_{artist_id}"
            topic_arn = f"arn:aws:sns:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:{topic_name}"

            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Subject=f"New song from {artist_id}!",
                    Message=f"A new song '{song_name}' was released by {artist_id}."
                )
                print(f"Published notification for {artist_id}")
            except Exception as e:
                print(f"Failed to notify for {artist_id}: {e}")

        for genre in genres:
            topic_name = f"genre_{genre}"
            topic_arn = f"arn:aws:sns:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:{topic_name}"

            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Subject=f"New {genre} song released!",
                    Message=f"A new {genre} song '{song_name}' was released."
                )
                print(f"Published notification for genre {genre}")
            except Exception as e:
                print(f"Failed to notify for genre {genre}: {e}")
