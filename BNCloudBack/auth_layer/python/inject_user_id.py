from authorization_exception import AuthorizationException


def inject_user_id(event: dict):
    authorizer = event.get('requestContext', {}).get('authorizer', {})
    claims = authorizer.get('claims', {})
    if not claims:
        raise AuthorizationException("No claims found in requestContext.authorizer")

    user_group = claims.get("cognito:groups")
    if not user_group:
        raise AuthorizationException("User has no assigned group")

    if isinstance(user_group, list):
        user_group = user_group[0]

    event["userRole"] = user_group
    event["userId"] = claims.get("sub")
    event["username"] = claims.get("cognito:username") or claims.get("preferred_username")
    event["email"] = claims.get("email")

    return claims
