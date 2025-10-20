import jwt

# Role to resource mapping
#RBAC MODEL -> We have roles and we have permissions what urls can what role CALL
ROLE_RULES = {
    "ADMIN": ["*"],  # full access
    "USER": ["arn:aws:execute-api:*:*:*/GET/public/*"],
}

SECRET = "your-secret"

def lambda_handler(event, context):
    token = event["headers"].get("Authorization", "").split(" ")[1]
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])

    role = decoded.get("role")
    method_arn = event["methodArn"]

    # Check access
    if not is_allowed(role, method_arn):
        return generate_policy(decoded["sub"], "Deny", method_arn)
    else:
        return generate_policy(decoded["sub"], "Allow", method_arn, decoded)


def is_allowed(role, method_arn):
    """Check if this role can access the requested ARN"""
    allowed_arns = ROLE_RULES.get(role, [])
    if "*" in allowed_arns:
        return True

    # Very basic match – can use fnmatch for pattern support
    import fnmatch
    for pattern in allowed_arns:
        if fnmatch.fnmatch(method_arn, pattern):
            return True
    return False


def generate_policy(principal_id, effect, resource, context_data=None):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource
            }]
        },
        "context": context_data or {}
    }
