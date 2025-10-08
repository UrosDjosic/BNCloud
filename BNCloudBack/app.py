#!/usr/bin/env python3
import aws_cdk as cdk
from bn_cloud_back.api_stack import ApiStack
from bn_cloud_back.auth_stack import AuthStack
enviroment = cdk.Environment(account='971422704654', region='eu-central-1')

app = cdk.App()
auth_stack = AuthStack(app, "AuthStack", env=enviroment)

api_stack = ApiStack(
    app, "ApiStack",
    user_pool=auth_stack.user_pool,
    user_pool_client= auth_stack.user_pool_client,
    env=enviroment
)


app.synth()
