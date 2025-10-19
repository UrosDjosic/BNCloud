from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb
class AlbumApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,other_tables, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Albums'
        }   
        album_resource = api.add_resource("album")
        util_layer =[ _lambda.LayerVersion(
            self, "UtilLambdaLayer",
            code=_lambda.Code.from_asset("libs"), 
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared utilities"
        )]

        lambda_role = iam.Role(
            self, "AlbumLambdaRole",
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
                    f"{other_tables['genre'].table_arn}/index/EntityTypeIndex",
                    other_tables['genre'].table_arn,
                    other_tables['artist'].table_arn
                ]
            )
        )


        #CREATE
        create_album_lambda = _lambda.Function(
            self, "CreateAlbumLambda",
            layers=util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="create_album.handler.create",
            code=_lambda.Code.from_asset("lambda/album"),
            environment=env,
            role = lambda_role
        )
        create_album_integration = apigw.LambdaIntegration(create_album_lambda)
        album_resource.add_method(
            "POST", create_album_integration
        )

        #GET
        album_id_resource = album_resource.add_resource("{albumId}")

        get_album_lambda = _lambda.Function(
            self, "GetAlbumLambda",
            layers=util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="get_album.get",  # fajl get_album.py i funkcija get(event, context)
            code=_lambda.Code.from_asset("lambda/album"),
            environment=env,
            role=lambda_role
        )

        get_album_integration = apigw.LambdaIntegration(get_album_lambda)
        album_id_resource.add_method("GET", get_album_integration)