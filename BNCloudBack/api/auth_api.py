# constructs/artist_api.py
from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_cognito as cognito,aws_iam as iam
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

class AuthApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.IResource,user_pool: cognito.UserPool,
                 user_pool_client: cognito.UserPoolClient
                 , **kwargs):
        super().__init__(scope, id, **kwargs)

        util_layer = [_lambda.LayerVersion(
            self, "UtilLambdaLayer",
            code=_lambda.Code.from_asset("libs"), 
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared utilities"
        )]

        # REGISTER LAMBDA
        register_lambda = _lambda.Function(
            self, "RegisterHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            layers=util_layer,
            handler="register.handler.register_handler",
            code=_lambda.Code.from_asset("lambda/auth"),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "CLIENT_ID": user_pool_client.user_pool_client_id
            },
        )
        register_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:AdminAddUserToGroup"],
                resources=[user_pool.user_pool_arn]
            )
        )
        user_pool.grant(register_lambda, "cognito-idp:SignUp")
        register_integration = apigw.LambdaIntegration(register_lambda)
        api.add_resource("register").add_method(
            "POST",register_integration,
            authorization_type=apigw.AuthorizationType.NONE
        )

        #Login lambda
        login_lambda = _lambda.Function(
            self, "LoginLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            layers=util_layer,
            handler="login.handler.main",
            code=_lambda.Code.from_asset("lambda/auth"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id, 
                "USER_POOL_ID": user_pool.user_pool_id
            },
        )
        user_pool.grant(login_lambda, "cognito-idp:AdminInitiateAuth")
        #Login!
        login_integration = apigw.LambdaIntegration(login_lambda)
        api.add_resource("login").add_method(
            "POST", login_integration,
            authorization_type=apigw.AuthorizationType.NONE
        )

        #Verify function lambda
        verify_lambda = _lambda.Function(
            self,"VerifyLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            layers=util_layer,
            handler = "verify_register.handler.verify_handler",
            code = _lambda.Code.from_asset("lambda/auth"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id, 
            },
        )
        user_pool.grant(verify_lambda,"cognito-idp:ConfirmSignUp")
        verify_integration = apigw.LambdaIntegration(verify_lambda)
        api.add_resource("verify").add_method(
            "PUT",verify_integration,
            authorization_type=apigw.AuthorizationType.NONE
        )


        #Refresh access token lambda
        refresh_lambda= _lambda.Function(
            self,"RefreshLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            layers=util_layer,
            handler = "refresh.handler.main",
            code = _lambda.Code.from_asset("lambda/auth"),
            environment={
                "CLIENT_ID": user_pool_client.user_pool_client_id, 
            },
        )
        refresh_integration = apigw.LambdaIntegration(refresh_lambda)
        api.add_resource("refresh").add_method(
            "PUT",refresh_integration
        )
        

