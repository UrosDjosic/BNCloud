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
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,notification_queue, 
                 layers ,feed_queue,**kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Subscriptions'
        }   
        subscription_resource = api.add_resource("subscription")


        lambda_role = iam.Role(
            self, "SubscriptionsLambdaRole",
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
                    "dynamodb:DeleteItem",
                    "sns:CreateTopic",
                    "sns:Subscribe",
                    "sns:Publish",
                    "sns:GetTopicAttributes",
                    "sns:ListSubscriptionsByTopic",
                    "sns:Unsubscribe"   

                ],
                resources=[
                    table.table_arn,
                    f"{table.table_arn}/index/user_email-index",
                    "arn:aws:sns:eu-central-1:971422704654:*"
                ]
            )
        )



        #SUBSCRIBE
        subscribe_lambda = _lambda.Function(
            self, "SubscribeLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="subscription.add_subscription.handler.add",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                'FEED_QUEUE_URL' : feed_queue.queue_url
            },
            role = lambda_role
        )
        subscribe_integration = apigw.LambdaIntegration(
            subscribe_lambda
        )
        subscription_resource.add_method(
            "POST",subscribe_integration
        )

        #UNSUBSCRIBE
        unsubscribe_lambda = _lambda.Function(
            self, "UnsubscribeLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="subscription.unsubscribe.handler.unsubscribe",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                'FEED_QUEUE_URL' : feed_queue.queue_url
            },
            role = lambda_role
        )
        unsubscribe_integration = apigw.LambdaIntegration(
            unsubscribe_lambda
        )
        subscription_resource.add_method(
            "PUT",unsubscribe_integration
        )


        #GET USER SUBSCRIPTIONS
        get_subscriptions_lambda = _lambda.Function(
            self,"GetSubscriptions",
            layers = layers,
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler="subscription.get_subscriptions.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            role = lambda_role
        )
        get_subscriptions_integration = apigw.LambdaIntegration(
            get_subscriptions_lambda
        )
        subscription_resource.add_resource("{userEmail}").add_method(
            "GET",get_subscriptions_integration
        )

        #NOTIFY
        notify_lambda = _lambda.Function(
            self, "NotifySubscribersLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="subscription.notify.handler.notify",
            code=_lambda.Code.from_asset("lambda"),
            environment = {
                'AWS_ACCOUNT_ID' : '971422704654',
            },
            role = lambda_role
        )
        notify_lambda.add_event_source(lambda_events.SqsEventSource(notification_queue))