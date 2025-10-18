#!/usr/bin/env python3
import aws_cdk as cdk
from bn_cloud_back.api_stack import ApiStack
from bn_cloud_back.auth_stack import AuthStack
from bn_cloud_back.storage_stack import StorageStack
enviroment = cdk.Environment(account='971422704654', region='eu-central-1')

app = cdk.App()
auth_stack = AuthStack(app, "AuthStack", env=enviroment)
storage_stack = StorageStack(app,"StorageStack",env=enviroment)
api_stack = ApiStack(
    app, "ApiStack",
    user_pool=auth_stack.user_pool,
    user_pool_client= auth_stack.user_pool_client,
    tables = storage_stack.tables,
    songs_bucket = storage_stack.songs_bucket,
    env=enviroment
)
app.synth()
