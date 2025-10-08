from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_apigateway as apigw,
    aws_lambda as _lambda
)



class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, user_pool, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        api = apigw.RestApi(
            self,
            "api",
            rest_api_name="api",
            description="API Gateway with Cognito Auth",
            deploy_options=apigw.StageOptions(stage_name="prod")
        )
        
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        api_resource = api.root.add_resource("api")
        
        secure = api_resource.add_resource("secure")
        secure.add_method(
            "GET",
            apigw.MockIntegration(
                integration_responses=[{"statusCode": "200"}],
                request_templates={"application/json": '{"statusCode": 200}'}
            ),
            method_responses=[{"statusCode": "200"}],
            authorizer=authorizer,     
            authorization_type=apigw.AuthorizationType.COGNITO
        )

        