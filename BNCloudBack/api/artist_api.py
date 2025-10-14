# constructs/artist_api.py
from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb
class ArtistApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Artists'
        }   
        artist_resource = api.add_resource("artist")


        lambda_role = iam.Role(
            self, "LambdaRole",
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
                resources=[table.table_arn]
            )
        )

    
        #CREATE
        create_artist_lambda = _lambda.Function(
            self, "CreateArtistLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="artist.create_artist.handler.create",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role
        )
        create_artist_integration = apigw.LambdaIntegration(create_artist_lambda)
        artist_resource.add_method(
            "POST", create_artist_integration
        )

        #GET
        get_artists_lambda = _lambda.Function(
            self,"GetArtistsLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler = "artist.get_artists.handler.get",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role)
        get_artists_integration = apigw.LambdaIntegration(get_artists_lambda)
        artist_resource.add_method(
            "GET",get_artists_integration
        )

        #UPDATE
        update_artist_lambda = _lambda.Function(
            self,"UpdateArtistLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            handler = "artist.update_artist.handler.update",
            code=_lambda.Code.from_asset("lambda"),
            environment=env,
            role = lambda_role)
        update_artist_integration = apigw.LambdaIntegration(update_artist_lambda)
        artist_resource.add_method(
            "PUT",update_artist_integration
        )
