from constructs import Construct
from aws_cdk import (aws_lambda as _lambda,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_dynamodb as dynamodb,
                     aws_s3 as s3,
                     Duration,
                     Size)
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
class SongApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table,other_tables, 
                 songs_bucket, transcribe_queue,notification_queue, **kwargs):
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
                    other_tables['genre'].table_arn,
                    other_tables['album'].table_arn
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


        #UPDATE
        update_song_lambda = _lambda.Function(
            self, "UpdateSongLambda",
            layers=util_layer,
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
