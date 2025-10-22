from constructs import Construct
from aws_cdk import (aws_lambda as _lambda,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_dynamodb as dynamodb)
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
class UserlistApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table, layers,  **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Userlists'
        }   
        userlist_resource = api.add_resource("userlist")
        userlist_id_resource = userlist_resource.add_resource("{userlistId}")
        userlist_user_resource = userlist_resource.add_resource("user")
        userlist_user_id_resource = userlist_user_resource.add_resource("{userId}")

        lambda_role = iam.Role(
            self, "UserlistsLambdaRole",
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

        #CREATE
        create_userlist_lambda = _lambda.Function(
            self, "CreateUserlistLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="userlist.create_userlist.handler.create",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        create_userlist_integration = apigw.LambdaIntegration(create_userlist_lambda)
        userlist_resource.add_method("POST", create_userlist_integration)

        #GET
        get_userlist_lambda = _lambda.Function(
            self, "GetUserlistLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="userlist.get_userlist.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        get_userlist_integration = apigw.LambdaIntegration(get_userlist_lambda)
        userlist_id_resource.add_method("GET", get_userlist_integration)

        #GET
        get_user_userlist_lambda = _lambda.Function(
            self, "GetUserUserlistLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="userlist.get_users.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        get_user_userlist_integration = apigw.LambdaIntegration(get_user_userlist_lambda)
        userlist_user_id_resource.add_method("GET", get_user_userlist_integration)


        #UPDATE
        update_userlist_lambda = _lambda.Function(
            self, "UpdateUserlistLambda",
            layers=layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="userlist.update_userlist.handler.update",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )

        update_userlist_integration = apigw.LambdaIntegration(update_userlist_lambda)
        userlist_id_resource.add_method("PUT", update_userlist_integration)