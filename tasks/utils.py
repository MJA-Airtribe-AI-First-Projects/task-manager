from rest_framework.response import Response


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
