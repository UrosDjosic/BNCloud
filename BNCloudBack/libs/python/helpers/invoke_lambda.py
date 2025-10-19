import boto3, json, os
lambda_client = boto3.client('lambda')

def invoke_target(fn, payload):
    response = lambda_client.invoke(
        FunctionName=fn,
        InvocationType='RequestResponse',  # wait for completion
        Payload=json.dumps(payload)
    )
    result = json.loads(response['Payload'].read())
    return result