from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb
class SongApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,other_tables, songs_bucket, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Songs'
        }   
        song_resource = api.add_resource("song")
        song_id_resource = song_resource.add_resource("{songId}")

        util_layer =[ _lambda.LayerVersion(
            self, "UtilLambdaLayer",
            code=_lambda.Code.from_asset("libs"), 
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared utilities"
        )]
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
                    table.table_arn,
                    other_tables['artist'].table_arn,
                    other_tables['genre'].table_arn
                ]
            )
        )

        #CREATE
        create_song_lambda = _lambda.Function(
            self, "CreateSongLambda",
            layers = util_layer,
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

        #GET
        get_song_lambda = _lambda.Function(
            self, "GetSongLambda",
            layers = util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.get_song.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        songs_bucket.grant_read(get_song_lambda)

        get_song_integration = apigw.LambdaIntegration(get_song_lambda)
        song_id_resource.add_method("GET", get_song_integration)