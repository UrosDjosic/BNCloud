import json
import boto3
import os
from helpers.create_response import create_response


client = boto3.client("cognito-idp")
CLIENT_ID = os.environ["CLIENT_ID"]
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:4200")

def main(event, context):
    body = json.loads(event.get("body", "{}"))
    refresh_token = body.get("refreshToken")
    if not refresh_token:
        return create_response(401, {"error": "Missing refresh token in cookies"})

    try:
        result = client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
            ClientId=CLIENT_ID,
        )

        auth_result = result.get("AuthenticationResult", {})
        return create_response(
            200,
            {
                "message": "Token refreshed",
                "accessToken": auth_result.get("AccessToken"),
                "idToken": auth_result.get("IdToken"),
            },
        )

    except client.exceptions.NotAuthorizedException:
        return create_response(401, {"error": "Invalid or expired refresh token"})

    except Exception as e:
        return create_response(500, {"error": str(e)})
