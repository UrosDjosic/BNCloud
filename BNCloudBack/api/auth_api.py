# constructs/artist_api.py
from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_cognito as cognito

class AuthApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.IResource,user_pool: cognito.UserPool,
                 user_pool_client: cognito.UserPoolClient
                 , **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda function
        register_lambda = _lambda.Function(
            self, "RegisterHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.register_handler",
            code=_lambda.Code.from_asset("lambda/register"),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "CLIENT_ID": user_pool_client.user_pool_client_id
            }
        )
        user_pool.grant(register_lambda, "cognito-idp:SignUp")
        register_integration = apigw.LambdaIntegration(register_lambda)
        api.add_resource("register").add_method(
            "POST",register_integration
        )


        login_lambda = _lambda.Function(
            self, "LoginLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda/login"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id, 
                "USER_POOL_ID": user_pool.user_pool_id
            },
        )
        user_pool.grant(login_lambda, "cognito-idp:AdminInitiateAuth")
        #Login!
        login_integration = apigw.LambdaIntegration(login_lambda)
        api.add_resource("login").add_method(
            "POST", login_integration
        )


