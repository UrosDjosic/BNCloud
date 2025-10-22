from constructs import Construct
from aws_cdk import (aws_lambda as _lambda,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_dynamodb as dynamodb,
                     aws_s3 as s3,
                     Duration, 
                     Stack,
                     Size)
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
class SongApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,other_tables, 
                 songs_bucket, transcribe_queue,notification_queue,
                 feed_queue,layers, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Songs'
        }   
        song_resource = api.add_resource("song")
        song_id_resource = song_resource.add_resource("{songId}")
        song_search_resource = song_resource.add_resource("search")
        song_name_resource = song_search_resource.add_resource("{name}")

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
                    other_tables['genre'].table_arn,
                    other_tables['album'].table_arn,
                    other_tables['ratings'].table_arn
                ]
            )
        )

        #CREATE
        create_song_lambda = _lambda.Function(
            self, "CreateSongLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.create_song.handler.create",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "QUEUE_URL": notification_queue.queue_url,
                "TABLE_NAME": "Songs",
            },
            role = lambda_role
        )

        notification_queue.grant_send_messages(create_song_lambda)

        songs_bucket.grant_put(create_song_lambda)

        create_song_integration = apigw.LambdaIntegration(create_song_lambda)
        song_resource.add_method(
            "POST", create_song_integration
        )

        #GET
        get_song_lambda = _lambda.Function(
            self, "GetSongLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.get_song.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FEED_QUEUE_URL": feed_queue.queue_url,
                "TABLE_NAME": "Songs",
            },
            role = lambda_role
        )
        feed_queue.grant_send_messages(get_song_lambda)
        songs_bucket.grant_read(get_song_lambda)

        get_song_integration = apigw.LambdaIntegration(get_song_lambda)
        song_id_resource.add_method("GET", get_song_integration)

        #GET /search/{name}
        search_song_lambda = _lambda.Function(
            self, "SearchSongLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.search_song.handler.search",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )

        search_song_integration = apigw.LambdaIntegration(search_song_lambda)
        song_name_resource.add_method("GET", search_song_integration)


        #UPDATE
        update_song_lambda = _lambda.Function(
            self, "UpdateSongLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.update_song.handler.update",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )

        songs_bucket.grant_read_write(update_song_lambda)
        table.grant_read_write_data(update_song_lambda)
        other_tables['artist'].grant_read_write_data(update_song_lambda)
        other_tables['genre'].grant_read_write_data(update_song_lambda)
        other_tables['album'].grant_read_write_data(update_song_lambda)

        update_song_integration = apigw.LambdaIntegration(update_song_lambda)

        song_id_resource.add_method("PUT", update_song_integration)

        # PUT /song/audio
        song_audio_resource = song_resource.add_resource("audio")

        update_song_audio_lambda = _lambda.Function(
            self, "UpdateSongAudioLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.update_audio.handler.update_audio",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )

        # Allow Lambda to upload to S3 and update DynamoDB
        songs_bucket.grant_read_write(update_song_audio_lambda)
        table.grant_read_write_data(update_song_audio_lambda)

        update_song_audio_integration = apigw.LambdaIntegration(update_song_audio_lambda)
        song_audio_resource.add_method("PUT", update_song_audio_integration)

        # PUT /song/image
        song_image_resource = song_resource.add_resource("image")

        update_song_image_lambda = _lambda.Function(
            self, "UpdateSongImageLambda",
            layers = layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.update_image.handler.update_image",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )

        # Allow Lambda to upload to S3 and update DynamoDB
        songs_bucket.grant_read_write(update_song_image_lambda)
        table.grant_read_write_data(update_song_image_lambda)

        update_song_image_integration = apigw.LambdaIntegration(update_song_image_lambda)
        song_image_resource.add_method("PUT", update_song_image_integration)

        # PUT /song/rate
        rate_song_resource = song_resource.add_resource("rate")
        rate_song_lambda = _lambda.Function(
            self, "RateSongLambda",
            layers=layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.rate_song.handler.rate",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        table.grant_read_write_data(rate_song_lambda)
        rate_song_integration = apigw.LambdaIntegration(rate_song_lambda)
        rate_song_resource.add_method("PUT", rate_song_integration)


        # TRANSCRIBE (containerized faster-whisper)
        transcribe_lambda = _lambda.DockerImageFunction(
            self,
            "TranscribeSongLambda",
            code=_lambda.DockerImageCode.from_image_asset(
                "lambda/song/transcribe_container"
            ),
            role=lambda_role,
            environment={
                "TABLE_NAME": 'Songs',
                "S3_BUCKET_NAME": songs_bucket.bucket_name,
                "WHISPER_MODEL": "medium",
                "WHISPER_COMPUTE": "int8",
                "WHISPER_BEAM_SIZE": "5",
                "WHISPER_BEST_OF": "5",
            },
            memory_size=3008,
            timeout=Duration.minutes(15),
            ephemeral_storage_size=Size.gibibytes(10),
        )
        # Allow Lambda to read audio objects
        songs_bucket.grant_read(transcribe_lambda)
        # Ensure Lambda can poll and delete messages from the queue
        transcribe_queue.grant_consume_messages(transcribe_lambda)
        # Consume S3 events via SQS to avoid cross-stack cycle
        transcribe_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(transcribe_queue, batch_size=1)
        )


        # Delete workers
        delete_song_from_artists_lambda = _lambda.Function(
            self, "DeleteSongFromArtistsLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.delete_song.from_artists.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        other_tables['artist'].grant_read_write_data(delete_song_from_artists_lambda)

        delete_song_from_albums_lambda = _lambda.Function(
            self, "DeleteSongFromAlbumsLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.delete_song.from_albums.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        other_tables['album'].grant_read_write_data(delete_song_from_albums_lambda)

        delete_song_from_s3_lambda = _lambda.Function(
            self, "DeleteSongFromS3Lambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.delete_song.from_s3.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role=lambda_role
        )
        songs_bucket.grant_read_write(delete_song_from_s3_lambda)

        # DELETE /song/{songId}
        delete_song_lambda = _lambda.Function(
            self, "DeleteSongLambda",
            layers=layers,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="song.delete_song.handler.delete",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": "Songs",
                "DELETE_SONG_FROM_ARTISTS": delete_song_from_artists_lambda.function_arn,
                "DELETE_SONG_FROM_ALBUMS": delete_song_from_albums_lambda.function_arn,
                "DELETE_SONG_FROM_S3": delete_song_from_s3_lambda.function_arn,
                "SONGS_BUCKET_NAME": songs_bucket.bucket_name,
            },
            role=lambda_role
        )

        for fn in [
            delete_song_from_artists_lambda,
            delete_song_from_albums_lambda,
            delete_song_from_s3_lambda
        ]:
            fn.add_permission(
                "AllowInvokeFromLambda",
                principal=iam.ServicePrincipal("lambda.amazonaws.com"),
                action="lambda:InvokeFunction",
                source_account=Stack.of(self).account
            )

        songs_bucket.grant_read_write(delete_song_lambda)
        table.grant_read_write_data(delete_song_lambda)
        other_tables['artist'].grant_read_write_data(delete_song_lambda)
        other_tables['album'].grant_read_write_data(delete_song_lambda)

        delete_song_integration = apigw.LambdaIntegration(delete_song_lambda)
        song_id_resource.add_method("DELETE", delete_song_integration)
