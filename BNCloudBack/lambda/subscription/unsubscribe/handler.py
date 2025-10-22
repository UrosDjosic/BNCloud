import os
import json
import boto3
from helpers.create_response import create_response
from pre_authorize import pre_authorize

TABLE_NAME = os.environ.get('TABLE_NAME', 'Subscriptions')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
sns = boto3.client('sns')


@pre_authorize(['User'])
def unsubscribe(event, context):
    """Unsubscribe user from SNS topic and remove record from DynamoDB."""
    try:
        # Parse body
        body_raw = event.get('body') or '{}'
        body = json.loads(body_raw) if isinstance(body_raw, str) else (body_raw or {})

        subject_id = body.get('subject_id') or body.get('subjectId') or body.get('subject')
        user_email = body.get('user_email') or body.get('email')
        subject_name = body.get('subject_name')
        sub_type = body.get('sub_type')

        if not subject_id or not user_email or not sub_type:
            return create_response(400, {'message': 'subject_id, sub_type, and user_email are required'})

        # Topic
        topic_name = f"{sub_type}_{subject_id}"
        topic = sns.create_topic(Name=topic_name)
        topic_arn = topic['TopicArn']

        #Getting all subs
        subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        unsubscribed = False
        
        #loop through Subscriptions to find user
        for sub in subs.get('Subscriptions', []):
            if sub.get('Endpoint') == user_email and sub.get('SubscriptionArn') != 'PendingConfirmation':
                sns.unsubscribe(SubscriptionArn=sub['SubscriptionArn'])
                unsubscribed = True
                break

        # Delete from DB
        table = dynamodb.Table(TABLE_NAME)
        table.delete_item(
            Key={
                'subject_id': str(subject_id),
                'user_email': str(user_email)
            }
        )


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

        message = f"Unsubscribed {user_email} and removed record from table." if unsubscribed \
            else f"No active subscription found for {user_email}, but record deleted."

        return create_response(200, {'message': message, 'topicArn': topic_arn})

    except Exception as e:
        return create_response(500, {'message': str(e)})
