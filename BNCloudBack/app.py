#!/usr/bin/env python3
import aws_cdk as cdk
from bn_cloud_back.bn_cloud_back_stack import BnCloudBackStack
from bn_cloud_back.auth_stack import AuthStack
from bn_cloud_back.api_stack import ApiStack

enviroment = cdk.Environment(account='971422704654', region='eu-central-1')

app = cdk.App()
auth_stack = AuthStack(app, "AuthStack", env=enviroment)

api_stack = ApiStack(
    app, "ApiStack",
    user_pool=auth_stack.user_pool,
    env=enviroment
)


app.synth()
