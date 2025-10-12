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
            index_name="GenreIndex",
            partition_key=dynamodb.Attribute(
                name="genre",
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
        #-------CONTENT TABLE ----------
        content_table = dynamodb.Table(
            self,"content",
            table_name="music_content",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        self.tables['content'] = content_table
        # Creating S3 bucket used for saving songs(music content)
        bucket = s3.Bucket(
            self, 
            "SongsBucket",
            bucket_name="kirdanovi-brodograditelji-bucket",  
            versioned=True,                            
            removal_policy=RemovalPolicy.DESTROY,   
            auto_delete_objects=True                   
        )
