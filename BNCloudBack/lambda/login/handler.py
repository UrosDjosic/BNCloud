import json
import boto3
import os
client = boto3.client("cognito-idp")

def create_response(status, body):
    return { 
        'statusCode': status, 
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body, default=str)
        }

USER_POOL_ID = os.environ["USER_POOL_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
def main(event, context):
    body = json.loads(event.get("body", "{}"))
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return {"statusCode": 400, "body": json.dumps({"error": "username and password required"})}

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
        return create_response(200,{"message": "Login successful",
                                "tokens": response.get("AuthenticationResult", {})})
    except client.exceptions.NotAuthorizedException:
        return create_response(401, {"error": "Invalid username or password"})

    except client.exceptions.UserNotFoundException:
        return create_response(404, {"error": "User not found"})
    except Exception as e:
        return create_response(400, {"message": str(e)})
