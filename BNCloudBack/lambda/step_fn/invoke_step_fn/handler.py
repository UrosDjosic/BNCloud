import boto3, json
lambda_client = boto3.client("lambda")
sfn = boto3.client('stepfunctions')
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:123456789012:stateMachine:UserEventWorkflow'

def invoke(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(body)
        )
    return {'status': 'ok'}
