#!/usr/bin/env python3
import aws_cdk as cdk
from bn_cloud_back.api_stack import ApiStack
from bn_cloud_back.auth_stack import AuthStack
from bn_cloud_back.storage_stack import StorageStack
from bn_cloud_back.sqs_stack import SQStack
from bn_cloud_back.step_fn_stack import StepFunctionStack

enviroment = cdk.Environment(account='971422704654', region='eu-central-1')

app = cdk.App()
auth_stack = AuthStack(app, "AuthStack", env=enviroment)
storage_stack = StorageStack(app, "StorageStack", env=enviroment)
sqs_stack = SQStack(app, "SQStack", env=enviroment)
step_fn_stack = StepFunctionStack(app,"StepFunctionStack",env=enviroment,feed_queue=sqs_stack.feed_queue,
                                  tables = storage_stack.tables)
api_stack = ApiStack(
    app, "ApiStack",
    user_pool=auth_stack.user_pool,
    user_pool_client= auth_stack.user_pool_client,
    tables = storage_stack.tables,
    songs_bucket = storage_stack.songs_bucket,
    transcribe_queue = storage_stack.transcribe_queue,
    notification_queue= sqs_stack.notification_queue,
    feed_queue = sqs_stack.feed_queue,
    env=enviroment
)
app.synth()
