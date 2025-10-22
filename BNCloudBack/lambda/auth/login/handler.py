import json
import boto3
import os
from helpers.create_response import create_response
client = boto3.client("cognito-idp")

USER_POOL_ID = os.environ["USER_POOL_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
def main(event, context):
    body = json.loads(event.get("body", "{}"))
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return create_response(400, {"error": "username and password required"})

    try:
        response = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )
        auth_result = response.get("AuthenticationResult", {})

        return create_response(
            200,
            {
                "message": "Login successful",
                "tokens": auth_result
            },
        )
    except client.exceptions.NotAuthorizedException:
        return create_response(401, {"error": "Invalid username or password"})

    except client.exceptions.UserNotFoundException:
        return create_response(404, {"error": "User not found"})
    except client.exceptions.UserNotConfirmedException:
        return create_response(403, {"error": "User not confirmed. Please verify your account."})
    except Exception as e:
        return create_response(400, {"message": str(e)})
