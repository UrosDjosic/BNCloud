import verify_role
import inject_user_id
from authorization_exception import AuthorizationException

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def pre_authorize(allowed_groups: list):
    def decorator(handler):
        def wrapper(event, context):
            try:
                verify_role.verify_role(event, allowed_groups)
                inject_user_id.inject_user_id(event)
                return handler(event, context)
            except AuthorizationException as e:
                return {
                    "statusCode": 401,
                    "headers": CORS_HEADERS,
                    "body": str(e)
                }
        return wrapper
    return decorator
