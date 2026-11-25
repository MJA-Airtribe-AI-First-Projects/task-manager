import json

from rest_framework import status
from rest_framework.response import Response

# In-memory idempotency store
idempotency_store = {}


def error_response(code, message, details, status):
    """Build the API's consistent nested error response."""
    return Response(
        {
            "error": {
                "code": str(code),
                "message": str(message),
                "details": details
            }
        },
        status=status
    )


def serializer_errors_to_details(errors):
    """Convert DRF's field error mapping into the API's details list."""
    details = []

    for field, issues in errors.items():

        for issue in issues:
            details.append({
                "field": str(field),
                "issue": str(issue)
            })

    return details


def get_request_body(request):
    """
    Generate a consistent representation of the request.
    Include the path so the same key cannot accidentally
    replay a response from another endpoint or task.
    """
    return json.dumps(
        {
            "path": request.path,
            "body": request.data
        },
        sort_keys=True,
        default=str
    )


def check_idempotency(request):
    """
    Check whether this request has already been processed.
    """
    key = request.headers.get("Idempotency-Key")

    if not key:
        return None, None

    body = get_request_body(request)

    if key in idempotency_store:
        stored_data = idempotency_store[key]

        if stored_data["body"] != body:
            return error_response(
                "IDEMPOTENCY_KEY_CONFLICT",
                "Idempotency key was already used with a different request body",
                [],
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ), key

        # Same key and same body: return previous response
        stored_response = stored_data["response"]

        return Response(
            stored_response["data"],
            status=stored_response["status"]
        ), key

    return None, key


def save_idempotency_response(key, body, response):
    """
    Store only successful responses.
    """
    if key and 200 <= response.status_code < 300:
        idempotency_store[key] = {
            "body": body,
            "response": {
                "data": response.data,
                "status": response.status_code
            }
        }
