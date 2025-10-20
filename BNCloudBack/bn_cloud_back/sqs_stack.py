from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    Duration,
)


class SQStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)


        notification_queue = sqs.Queue(
            self, "NotificationQueue",
            visibility_timeout=Duration.seconds(60),
            retention_period=Duration.hours(1)
        )
        self.notification_queue = notification_queue

        # Transcribe queue is created in StorageStack to avoid cross-stack cycles

