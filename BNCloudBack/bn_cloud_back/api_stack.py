# api_stack.py
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_lambda as _lambda
)

from api.album_api import AlbumApi
from api.auth_api import AuthApi
from api.artist_api import ArtistApi
from api.song_api import SongApi
from api.genres_api import GenreApi
from api.subscriptions_api import SubscriptionsApi
from api.userlist_api import UserlistApi

class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, *, user_pool : cognito.UserPool, user_pool_client,tables, songs_bucket, transcribe_queue,
                 notification_queue,feed_queue, **kwargs):
        super().__init__(scope, id, **kwargs)

        #AUTHORIZER INIT
        cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name="BNCloudCognitoAuthorizer",
            identity_source="method.request.header.Authorization"
        )


        #API GATEWAY INIT
        api = apigw.RestApi(
            self,
            "api",
            rest_api_name="BNCloudApi",
            description="API Gateway with Cognito Auth",
            deploy_options=apigw.StageOptions(stage_name="prod"),
            default_cors_preflight_options=apigw.CorsOptions(
            allow_origins=apigw.Cors.ALL_ORIGINS,
            allow_methods=["OPTIONS", "GET", "POST", "PUT","DELETE"],), 
            default_method_options=apigw.MethodOptions(
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer
            )
        )
        api.add_gateway_response(
            "Default4xxResponse",
            type=apigw.ResponseType.DEFAULT_4_XX,
            response_headers={
                "Access-Control-Allow-Origin": "'http://localhost:4200'",
                "Access-Control-Allow-Credentials": "'true'",
                "Access-Control-Allow-Headers": "'*'",
                "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
            }
        )


        #INITIALIZING UTIL LAYER AND AUTH LAYER
        util_layer = _lambda.LayerVersion(
            self, "UtilLambdaLayer",
            code=_lambda.Code.from_asset("libs"), 
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared utilities"
        )
        auth_layer = _lambda.LayerVersion(
            self, "AuthLayer",
            code=_lambda.Code.from_asset("auth_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Authorization layer"
        )

        layers = [util_layer,auth_layer]

        root_api = api.root.add_resource("api")
        auth_api = AuthApi(
            self, 
            "AuthApi",
            api=root_api,
            user_pool=user_pool,
            user_pool_client=user_pool_client,
        )
        artist_api = ArtistApi(
            self,
            "ArtistApi",
            api = root_api,
            table = tables['artist'],
            other_tables = tables,
            layers = layers,
        )
        song_api = SongApi(
            self,
            "SongApi",
            api = root_api,
            table = tables['song'],
            other_tables= tables,
            songs_bucket = songs_bucket,
            transcribe_queue = transcribe_queue,
            notification_queue= notification_queue,
            layers = layers,
            feed_queue= feed_queue
        )
        album_api = AlbumApi(
            self,
            "AlbumApi",
            api = root_api,
            table = tables['album'],
            other_tables=tables,
            layers = layers,
            other_lambdas = {
                "delete_song_lambda": song_api.delete_song_lambda  
            }
        )
        album_api.node.add_dependency(song_api)
        genre_api = GenreApi(
            self,
            "GenreApi",
            api = root_api,
            table = tables['genre'],
            layers = layers
        )
        subscriptions_api = SubscriptionsApi(
            self,
            "SubscriptionsApi",
            api = root_api,
            table = tables['subscription'],
            notification_queue= notification_queue,
            layers = layers,
            feed_queue=feed_queue
        )
        userlist_api = UserlistApi(
            self,
            "UserlistApi",
            api = root_api,
            table = tables['userlist'],
            layers = layers
        )
