import json
import boto3
import os
from helpers.create_response import create_response

client = boto3.client("cognito-idp")
CLIENT_ID = os.environ["CLIENT_ID"]

# Helper func to extract token
def extract_refresh_token(event):
    # HTTP API format
    if "cookies" in event and event["cookies"]:
        for c in event["cookies"]:
            if c.startswith("RefreshToken="):
                return c.split("=", 1)[1]

    # REST API format
    cookie_header = event.get("headers", {}).get("Cookie") or event.get("headers", {}).get("cookie")
    if cookie_header:
        for c in cookie_header.split(";"):
            if "RefreshToken=" in c:
                return c.split("=", 1)[1].strip()

    return None


def main(event, context):
    refresh_token = extract_refresh_token(event)

    if not refresh_token:
        return create_response(401, {"error": "Missing refresh token in cookies"})

    try:
        response = client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
            ClientId=CLIENT_ID,
        )

        auth_result = response.get("AuthenticationResult", {})
        new_access_token = auth_result.get("AccessToken")
        new_id_token = auth_result.get("IdToken")
        return create_response(
            200,
            {
                "message": "Token refreshed",
                "accessToken": new_access_token,
                "idToken": new_id_token,
            },
        )

    except client.exceptions.NotAuthorizedException:
        return create_response(401, {"error": "Invalid or expired refresh token"})
    except Exception as e:
        return create_response(500, {"error": str(e)})
