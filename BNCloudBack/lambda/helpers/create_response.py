import json
import json

def create_response(status, body, headers=None):
    base_headers = {
        'Access-Control-Allow-Origin': '*',
    }

    if headers:
        base_headers.update(headers)

    return {
        'statusCode': status,
        'headers': base_headers,
        'body': json.dumps(body, default=str)
    }
