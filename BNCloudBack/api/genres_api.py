from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_iam as iam,aws_dynamodb as dynamodb

class GenreApi(Construct):
    def __init__(self, scope: Construct, id: str, *, api: apigw.RestApi,table, 
                 layers, **kwargs):
        super().__init__(scope, id, **kwargs)
        env = {
                "TABLE_NAME" : 'Genres'
        }       

        genre_resource = api.add_resource("genre")


        lambda_role = iam.Role(
            self, "GenresLambdaRole",
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
                    f"{table.table_arn}/index/EntityTypeIndex"
                ]
            )
        )   

        #GET ALL (OR ONE)
        get_lambda = _lambda.Function(
            self,"GetGenreLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            layers = layers,
            handler= "get_genres.handler.get",
            code = _lambda.Code.from_asset("lambda/genre"),
            environment = env,
            role = lambda_role,
        )
        get_integration = apigw.LambdaIntegration(get_lambda)
        genre_resource.add_method(
            "GET", get_integration,
        )

        #DISCOVER
        discover_lambda = _lambda.Function(self,"DiscoverLambda",
            runtime = _lambda.Runtime.PYTHON_3_11,
            layers = layers,
            handler= "discover.handler.discover",
            code = _lambda.Code.from_asset("lambda/genre"),
            environment = env,
            role = lambda_role
        )
        discover_integration = apigw.LambdaIntegration(discover_lambda)
        genre_resource.add_resource("discover").add_method(
            "GET", discover_integration
        )