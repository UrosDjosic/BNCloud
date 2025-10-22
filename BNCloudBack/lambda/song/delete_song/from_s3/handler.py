import boto3
import json

s3_client = boto3.client('s3')


def delete(event, context):
    bucket = event.get('bucket') or 'songs-bucket-1'
    audio_key = event.get('audioKey')
    image_key = event.get('imageKey')

    deleted = []

    try:
        if audio_key:
            s3_client.delete_object(Bucket=bucket, Key=audio_key)
            deleted.append(audio_key)
        if image_key:
            s3_client.delete_object(Bucket=bucket, Key=image_key)
            deleted.append(image_key)
    except Exception as e:
        print(f"Error deleting from S3: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 200, "body": json.dumps({"deleted_keys": deleted})}
