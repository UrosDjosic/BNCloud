import boto3
import json
import os

STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN")
if STATE_MACHINE_ARN:
    region = STATE_MACHINE_ARN.split(":")[3]  # extract eu-central-1, etc.
    sfn = boto3.client("stepfunctions", region_name=region)
else:
    raise ValueError("Environment variable STATE_MACHINE_ARN not set")

lambda_client = boto3.client("lambda")

def invoke(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(body)
        )
    return {"status": "ok"}
