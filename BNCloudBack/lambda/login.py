import json
import boto3
import os

client = boto3.client("cognito-idp")
CLIENT_ID = os.environ["CLIENT_ID"]

def main(event, context):
    body = json.loads(event.get("body", "{}"))
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "username and password required"})
        }

    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password
            }
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Login successful",
                "tokens": response["AuthenticationResult"]
            })
        }

    except client.exceptions.NotAuthorizedException:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid username or password"})
        }
    except client.exceptions.UserNotFoundException:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "User not found"})
        }
