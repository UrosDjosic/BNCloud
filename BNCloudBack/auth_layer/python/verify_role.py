from authorization_exception import AuthorizationException


def verify_role(event: dict, allowed_groups: list):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    if not claims:
        raise AuthorizationException("No claims found in requestContext.authorizer")

    user_group = claims.get("cognito:groups")
    if not user_group:
        raise AuthorizationException("User has no assigned group")

    if isinstance(user_group, list):
        user_group = user_group[0]

    if user_group not in allowed_groups:
        raise AuthorizationException(f"User not authorized for group: {user_group}")

    event["userId"] = claims.get("sub")
    return claims