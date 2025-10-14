from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb

class ArtistApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Artists'
        }   
        genre_resource = api.add_resource("genre")


        lambda_role = iam.Role(
            self, "ArtistLambdaRole",
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
                resources=[table.table_arn]
            )
        )   

        #CREATE GENRE LAMBDA
        create_lambda = _lambda.Function(
            self,"CreateGenreLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler= "",
            code = _lambda.Code.from_asset("genre.lambda"),
            enviroment = env,
            role = lambda_role
        )
        create_integration = apigw.LambdaIntegration(create_lambda)
        genre_resource.create_method(
            "POST",create_integration
        )