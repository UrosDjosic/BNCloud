from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    RemovalPolicy
)


class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.tables = {}
        
        #--------------- ARTISTS TABLE CREATION ----------------
        artist_table = dynamodb.Table(
            self, "artists",
            table_name="Artists",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        self.tables['artist'] = artist_table
        
        artist_table.add_global_secondary_index(
            index_name="EntityTypeIndex",
            partition_key=dynamodb.Attribute(
                name="EntityType",  
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="name",  
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        
        
        
        #---------ALBUM TABLE -----------
        album_table = dynamodb.Table(
            self, "albums",
            table_name="Albums",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        self.tables['album'] = album_table

        #---------SONGS TABLE -----------
        song_table = dynamodb.Table(
            self, "songs",
            table_name="Songs",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        self.tables['song'] = song_table


        #---------GENRES TABLE-------------
        genre_table = dynamodb.Table(
            self, "genres",
            table_name="Genres",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        genre_table.add_global_secondary_index(
            index_name="EntityTypeIndex",
            partition_key=dynamodb.Attribute(
                name="EntityType",  
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="name",  
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        self.tables['genre'] = genre_table


        #--------------- SUBSCRIPTIONS TABLE -------------------------
        subscription_table = dynamodb.Table(
            self, "Subscriptions",
            table_name="Subscriptions",
            partition_key=dynamodb.Attribute(
                name="subject_id",  
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="user_email",  
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        self.tables['subscription'] = subscription_table




        #--------------- S3 BUCKET CREATION WITH CORS ----------------
        bucket = s3.Bucket(
            self, 
            "SongsBucket",
            bucket_name="songs-bucket-1",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.POST,
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.DELETE,
                        s3.HttpMethods.HEAD
                    ],
                    # very permissive origin; change to your frontend origin if using credentials
                    allowed_origins=["*"],
                    # allow common S3 headers clients send when uploading with presigned URLs
                    allowed_headers=[
                        "*",
                        "Content-Type",
                        "Content-MD5",
                        "x-amz-acl",
                        "x-amz-meta-*"
                    ],
                    # expose S3 response headers so the browser JS can read them after upload
                    exposed_headers=[
                        "ETag",
                        "x-amz-request-id",
                        "x-amz-id-2",
                        "x-amz-version-id",
                        "x-amz-server-side-encryption",
                        "x-amz-expiration"
                    ],
                )
            ]
        )
        self.songs_bucket = bucket

        transcribe_queue = sqs.Queue(
            self,
            "SongsTranscribeQueue",
            visibility_timeout=Duration.minutes(15),
            retention_period=Duration.days(2),
        )
        self.transcribe_queue = transcribe_queue

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SqsDestination(transcribe_queue),
        )

