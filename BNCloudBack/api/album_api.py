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
                    other_tables['artist'].table_arn,
                    other_tables['song'].table_arn,
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
            handler="get_album.handler.get",  
            code=_lambda.Code.from_asset("lambda/album"),
            environment=env,
            role=lambda_role
        )

        get_album_integration = apigw.LambdaIntegration(get_album_lambda)
        album_id_resource.add_method("GET", get_album_integration)

        #PUT
        update_album_lambda = _lambda.Function(
            self, "UpdateAlbumLambda",
            layers=util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="update_album.handler.update",
            code=_lambda.Code.from_asset("lambda/album"),
            environment=env,
            role=lambda_role
        )

        update_album_integration = apigw.LambdaIntegration(update_album_lambda)
        album_id_resource.add_method("PUT", update_album_integration)


         #DELETE 

        delete_album_from_artists_lambda = _lambda.Function(
            self, "DeleteAlbumFromArtistsLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="album.delete_album.from_artists.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        other_tables['artist'].grant_read_write_data(delete_album_from_artists_lambda)

        delete_album_from_genres_lambda = _lambda.Function(
            self, "DeleteAlbumFromGenresLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="album.delete_album.from_genres.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        other_tables['genre'].grant_read_write_data(delete_album_from_genres_lambda)

        delete_album_from_songs_lambda = _lambda.Function(
            self, "DeleteAlbumFromSongsLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="album.delete_album.from_songs.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        other_tables['song'].grant_read_write_data(delete_album_from_songs_lambda)


        delete_album_lambda = _lambda.Function(
            self, "DeleteAlbumLambda",
            layers=util_layer,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="album.delete_album.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": "Albums",
                "DELETE_ALBUM_FROM_ARTISTS": delete_album_from_artists_lambda.function_arn,
                "DELETE_ALBUM_FROM_GENRES": delete_album_from_genres_lambda.function_arn,
                "DELETE_ALBUM_FROM_SONGS": delete_album_from_songs_lambda.function_arn
            },
            role=lambda_role
        )

        delete_album_from_artists_lambda.grant_invoke(delete_album_lambda)
        delete_album_from_genres_lambda.grant_invoke(delete_album_lambda)
        delete_album_from_songs_lambda.grant_invoke(delete_album_lambda)

        table.grant_read_write_data(delete_album_lambda)
        other_tables['artist'].grant_read_write_data(delete_album_lambda)
        other_tables['genre'].grant_read_write_data(delete_album_lambda)
        other_tables['song'].grant_read_write_data(delete_album_lambda)

        delete_album_integration = apigw.LambdaIntegration(delete_album_lambda)
        album_id_resource.add_method("DELETE", delete_album_integration)