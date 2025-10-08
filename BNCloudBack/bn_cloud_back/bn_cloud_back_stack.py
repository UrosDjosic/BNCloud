from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_dynamodb as dynamo,
    aws_apigateway as apigateway
)


class BnCloudBackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        api = apigateway.RestApi(
            self, "api",
            rest_api_name="api",
            description="API Gateway created imperatively via CDK"
        )
