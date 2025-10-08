# api_stack.py
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_cognito as cognito
)

from api.auth_api import AuthApi


class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, *, user_pool : cognito.UserPool, user_pool_client, **kwargs):
        super().__init__(scope, id, **kwargs)

        api = apigw.RestApi(
            self,
            "api",
            rest_api_name="BNCloudApi",
            description="API Gateway with Cognito Auth",
            deploy_options=apigw.StageOptions(stage_name="prod"),
        )

        root_api = api.root.add_resource("api")
        auth_api = AuthApi(
            self, 
            "AuthApi",
            api=root_api,
            user_pool=user_pool,
            user_pool_client=user_pool_client,
        )