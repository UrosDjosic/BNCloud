import json
import boto3
import os

client = boto3.client("cognito-idp")
CLIENT_ID = os.environ["CLIENT_ID"]
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:4200")  # 👈 fallback for local dev


def extract_refresh_token(event):
    if "cookies" in event and event["cookies"]:
        for c in event["cookies"]:
            if c.startswith("RefreshToken="):
                return c.split("=", 1)[1]

    cookie_header = event.get("headers", {}).get("Cookie") or event.get("headers", {}).get("cookie")
    if cookie_header:
        for c in cookie_header.split(";"):
            if "RefreshToken=" in c:
                return c.split("=", 1)[1].strip()

    return None


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": FRONTEND_URL,       
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,Origin,Accept",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
        },
        "body": json.dumps(body),
    }


def main(event, context):
    # Handle preflight requests directly (optional but good)
    if event.get("httpMethod") == "OPTIONS":
        return response(200, {"message": "CORS preflight OK"})

    refresh_token = extract_refresh_token(event)
    if not refresh_token:
        return response(401, {"error": "Missing refresh token in cookies"})

    try:
        result = client.initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
            ClientId=CLIENT_ID,
        )

        auth_result = result.get("AuthenticationResult", {})
        return response(
            200,
            {
                "message": "Token refreshed",
                "accessToken": auth_result.get("AccessToken"),
                "idToken": auth_result.get("IdToken"),
            },
        )

    except client.exceptions.NotAuthorizedException:
        return response(401, {"error": "Invalid or expired refresh token"})

    except Exception as e:
        return response(500, {"error": str(e)})
