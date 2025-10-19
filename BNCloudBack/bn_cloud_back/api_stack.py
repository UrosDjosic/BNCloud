# api_stack.py
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_cognito as cognito
)

from api.album_api import AlbumApi
from api.auth_api import AuthApi
from api.artist_api import ArtistApi
from api.song_api import SongApi
from api.genres_api import GenreApi

class ApiStack(Stack):
    def __init__(self, scope: Construct, id: str, *, user_pool : cognito.UserPool, user_pool_client,tables, songs_bucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        api = apigw.RestApi(
            self,
            "api",
            rest_api_name="BNCloudApi",
            description="API Gateway with Cognito Auth",
            deploy_options=apigw.StageOptions(stage_name="prod"),
            default_cors_preflight_options=apigw.CorsOptions(
            allow_origins=apigw.Cors.ALL_ORIGINS,
            allow_methods=["OPTIONS", "GET", "POST", "PUT"],)
        )

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
            other_tables = tables
        )
        song_api = SongApi(
            self,
            "SongApi",
            api = root_api,
            table = tables['song'],
            other_tables= tables,
            songs_bucket = songs_bucket
        )
        album_api = AlbumApi(
            self,
            "AlbumApi",
            api = root_api,
            table = tables['album'],
            other_tables=tables,
        )
        genre_api = GenreApi(
            self,
            "GenreApi",
            api = root_api,
            table = tables['genre']
        )