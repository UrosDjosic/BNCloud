from aws_cdk import (
    aws_lambda as _lambda,
    Duration,
    BundlingOptions
)

def create_lambda_function(construct,id, handler, include_dir, method, layers,table,lambda_role):
        _lambda.Function(
            construct, "CreateArtistLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler=handler,
            code=_lambda.Code.from_asset("lambda"),
            environment={
            },
        )