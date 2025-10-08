# constructs/artist_api.py
from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw

class ArtistApiConstruct(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi, table_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda function
        artist_lambda = _lambda.Function(
            self, "ArtistHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="artist.handler",
            code=_lambda.Code.from_asset("lambda/artist"),
            environment={
                "TABLE_NAME": table_name
            }
        )

        # API resource
        artist_resource = api.root.add_resource("artists")
        artist_resource.add_method(
            "GET",
            apigw.LambdaIntegration(artist_lambda)
        )
