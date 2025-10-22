import json
import boto3
import logging
import os
from helpers.create_response import create_response

from pre_authorize import pre_authorize  # assuming you use this for authentication

dynamodb = boto3.resource('dynamodb')
USER_FEED_TABLE = os.environ.get("TABLE_NAME")
table = dynamodb.Table(USER_FEED_TABLE)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pre_authorize(['Administrator','User'])
def init(event, context):
    """
    Lambda handler to return all items where pk = user_id.
    Expects event['pathParameters']['user_id'].
    """
    try:
        path_params = event.get('pathParameters') or {}
        user_id = path_params.get('userId')

        # Query DynamoDB by partition key
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("username").eq(user_id)
        )   

        items = response.get("Items", [])

        return create_response(200,items)
    except KeyError:
        logger.error("Missing path parameter: user_id")
        return create_response(400,{"error": "Missing user_id in pathParameters"})
    except Exception as e:
        logger.exception("Error querying DynamoDB")
        return create_response(500, {"error": str(e)})
