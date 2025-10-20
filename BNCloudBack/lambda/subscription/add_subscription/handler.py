import os
import json
import boto3
from datetime import datetime
from helpers.create_response import create_response

TABLE_NAME = os.environ.get('TABLE_NAME', 'Subscriptions')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def add(event, context):
    """Create a subscription and SNS email subscription."""
    try:
        # Parse body
        body_raw = event.get('body') or '{}'
        body = json.loads(body_raw) if isinstance(body_raw, str) else (body_raw or {})

        subject_id = body.get('subject_id') or body.get('subjectId') or body.get('subject')
        user_email = body.get('user_email') or body.get('email')

        if not subject_id or not user_email:
            return create_response(400, {'message': 'subject_id and user_email are required'})

        # 1️⃣ Save to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        item = {
            'subjectId': str(subject_id),
            'userEmail': str(user_email),
            'createdAt': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)

        # CREATE SNS TOPIC/REUSE
        topic_name = f"artist_{subject_id}"
        topic = sns.create_topic(Name=topic_name)
        topic_arn = topic['TopicArn']

        # SUB TO USER EMAIL
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=user_email
        )

        return create_response(200, {
            'message': f'Subscription created. Confirmation email sent to {user_email}.',
            'topicArn': topic_arn,
            'item': item
        })

    except Exception as e:
        return create_response(500, {'message': str(e)})
