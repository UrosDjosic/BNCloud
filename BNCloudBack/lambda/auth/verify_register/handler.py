import json
import boto3
import os
from helpers.create_response import create_response


# Initialize Cognito client
client = boto3.client('cognito-idp')
CLIENT_ID = os.environ['CLIENT_ID']       

"""
    Lambda function to verify registered user using code
    Expected body keys => username,code
"""
def verify_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        code= body['code']
        username = body['username']

        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=code,
        )

        return create_response(200,json.dumps({
                "message": "Account succesfully activated!",
                "response" : response
            }))

    except client.exceptions.CodeMismatchException:
        return create_response(404, json.dumps({"message": "Invalid verification code"}))
    except client.exceptions.ExpiredCodeException:
        return create_response(403, json.dumps({"message": "Verification code expired"}))
    except Exception as e:
        return create_response(500, json.dumps({"message": str(e)}))