from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb
class SongApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table, songs_bucket, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Songs'
        }   
        song_resource = api.add_resource("song")


        lambda_role = iam.Role(
            self, "LambdaRole",
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

        #CREATE
        create_song_lambda = _lambda.Function(
            self, "CreateSongLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.create_song.handler.create",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        songs_bucket.grant_put(create_song_lambda)

        create_song_integration = apigw.LambdaIntegration(create_song_lambda)
        song_resource.add_method(
            "POST", create_song_integration
        )