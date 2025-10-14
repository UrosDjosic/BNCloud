import json
import boto3
import os
from helpers.create_response import create_response


# Initialize Cognito client
client = boto3.client('cognito-idp')

USER_POOL_ID = os.environ['USER_POOL_ID']  
CLIENT_ID = os.environ['CLIENT_ID']       

def register_handler(event, context):
    """
    Lambda function to register a user in Cognito
    Expects event to have JSON with "username", "password", and "email"
    """
    try:
        body = json.loads(event.get('body', '{}'))
        username = body['username']
        password = body['password']
        email = body['email']
        firstName = body['firstName']
        lastName = body['lastName']
        birthdate = body['birthDate']

        response = client.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name' : 'custom:firstName',
                    'Value' : firstName
                },
                {
                    'Name' : 'custom:lastName',
                    'Value' : lastName
                },
                {
                    'Name' : 'birthdate',
                    'Value' : birthdate
                }
            ]
        )

        return create_response(200,json.dumps({
                "message": "User registration successful",
                "user_sub": response['UserSub']
            }))

    except client.exceptions.UsernameExistsException:
        return create_response(400,"User with same username already exists!")
    except Exception as e:
        return create_response(400,json.dumps({"message": str(e)}))
