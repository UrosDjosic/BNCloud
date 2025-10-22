import os
import json
import boto3
from datetime import datetime
from helpers.create_response import create_response
from pre_authorize import pre_authorize

TABLE_NAME = os.environ.get('TABLE_NAME', 'Subscriptions')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
sqs = boto3.client('sqs')

@pre_authorize(['User'])
def add(event, context):
    """Create a subscription and SNS email subscription."""
    try:
        # Parse body
        body_raw = event.get('body') or '{}'
        body = json.loads(body_raw) if isinstance(body_raw, str) else (body_raw or {})

        subject_id = body.get('subject_id') or body.get('subjectId') or body.get('subject')
        subject_name = body.get('subject_name') or body.get('subjectName')
        user_email = body.get('user_email') or body.get('email')
        sub_type = body.get('sub_type')

        if not subject_id or not user_email or not sub_type or not subject_name:
            return create_response(400, {'message': 'subject_id and user_email are required'})

        # 1️⃣ Save to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        item = {
            'subject_id': str(subject_id),
            'user_email': str(user_email),
            'subject_name' : str(subject_name),
            'sub_type' : str(sub_type),
            'createdAt': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)

        # CREATE SNS TOPIC/REUSE
        topic_name = f"{sub_type}_{subject_id}"
        topic = sns.create_topic(Name=topic_name)
        topic_arn = topic['TopicArn']

        # SUB TO USER EMAIL
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=user_email
        )
    
        
        if event['userRole'] == 'User':
            sqs.send_message(
                QueueUrl=os.environ["FEED_QUEUE_URL"],
                MessageBody=json.dumps({
                    "event_type": "user_subscribed",
                    "user_id": event["userId"],
                    "entity_type": sub_type,
                    "entity": {
                        'id' : subject_id,
                        'name' : subject_name
                    }
                })
            )

    
        return create_response(200, {
            'message': f'Subscription created. Confirmation email sent to {user_email}.',
            'topicArn': topic_arn,
            'item': item
        })

    except Exception as e:
        return create_response(500, {'message': str(e)})
