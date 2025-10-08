from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_cognito as cognito
)
from constructs import Construct

class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="BNCloudUserPool",
            self_sign_up_enabled=True,                     
            sign_in_aliases=cognito.SignInAliases(email=True), 
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_uppercase=True,
                require_lowercase=True,
                require_digits=True,
                require_symbols=False
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        admin_group = cognito.CfnUserPoolGroup(
            self, "AdminGroup",
            group_name="Administrator",
            user_pool_id=self.user_pool.user_pool_id,
            description="Administrators of the app"
        )
        user_group = cognito.CfnUserPoolGroup(
            self, "UserGroup",
            group_name="User",
            user_pool_id=self.user_pool.user_pool_id,
            description="Regular users of the app"
        )

        self.user_pool_client = self.user_pool.add_client(
            "AppClient",
            user_pool_client_name="WebClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=["http://localhost:4200/callback"],
                logout_urls=["http://localhost:4200/logout"],
            )
        )


        self.identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                {
                    "clientId": self.user_pool_client.user_pool_client_id,
                    "providerName": self.user_pool.user_pool_provider_name,
                }
            ],
        )
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
        CfnOutput(self, "IdentityPoolId", value=self.identity_pool.ref)
