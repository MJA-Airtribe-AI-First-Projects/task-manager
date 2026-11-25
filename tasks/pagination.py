from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    """Use page-number pagination with a client-adjustable, capped page size."""

    page_size = 10
    # Allow clients to request a different page size through the query string.
    page_size_query_param = 'page_size'
    # Prevent a request from returning an excessively large page.
    max_page_size = 100
