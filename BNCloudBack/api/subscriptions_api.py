from constructs import Construct
from aws_cdk import (aws_lambda as _lambda,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_dynamodb as dynamodb,
                     aws_s3 as s3,
                    aws_lambda_event_sources as lambda_events,
                     Duration,
                     Size)


class SubscriptionsApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,notification_queue, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Subscriptions'
        }   
        subscription_resource = api.add_resource("subscription")


        lambda_role = iam.Role(
            self, "SongsLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:DescribeTable",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem"
                ],
                resources=[
                    table.table_arn
                ]
            )
        )

        util_layer =[ _lambda.LayerVersion(
            self, "UtilLambdaLayer",
            code=_lambda.Code.from_asset("libs"), 
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared utilities"
        )]

        #SUBSCRIBE
        subscribe_lambda = _lambda.Function(
            self, "SubscribeLambda",
            layers = util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="subscription.add_subscription.handler.add",
            code=_lambda.Code.from_asset("lambda"),
            role = lambda_role
        )
        subscribe_integration = apigw.LambdaIntegration(
            subscribe_lambda
        )
        subscription_resource.add_method(
            "POST",subscribe_integration
        )


        #NOTIFY
        notify_lambda = _lambda.Function(
            self, "NotifySubscribersLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="subscription.notify.handler.notify",
            code=_lambda.Code.from_asset("lambda"),
        )
        notify_lambda.add_event_source(lambda_events.SqsEventSource(notification_queue))