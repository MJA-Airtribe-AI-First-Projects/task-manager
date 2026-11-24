import logging
from typing import override

from django.db import transaction
from django.http import Http404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .ai import parse_task_text, break_down_task
from .models import Task
from .serializers import TaskSerializer
from .utils import error_response, serializer_errors_to_details

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    """Provide CRUD operations for tasks with a consistent error format."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # def handle_exception(self, exc):
    #     """Normalize DRF validation and not-found errors for every action."""
    #     response = super().handle_exception(exc)
    #
    #     if response.status_code == status.HTTP_400_BAD_REQUEST:
    #         return error_response(
    #             "VALIDATION_ERROR",
    #             "Validation failed",
    #             serializer_errors_to_details(response.data),
    #             status.HTTP_400_BAD_REQUEST,
    #         )
    #
    #     if response.status_code == status.HTTP_404_NOT_FOUND:
    #         return error_response(
    #             "NOT_FOUND",
    #             "Task not found",
    #             [],
    #             status.HTTP_404_NOT_FOUND,
    #         )
    #
    #     return response

    # These methods are overridden to follow the assignment instructions;
    # the same error handling could otherwise be centralized in handle_exception.
    @override
    def retrieve(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
        except Http404:
            # Return missing-object errors using the API's standard envelope.
            return error_response(
                "NOT_FOUND",
                "Task not found",
                [],
                status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    @override
    def create(self, request, *args, **kwargs):

        if request.data.get("parent") not in (None, ""):
            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                [{
                    "field": "parent",
                    "issue": "Subtasks cannot be created through this endpoint."
                }],
                status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            # Convert DRF's field errors into the API's details list.
            details = serializer_errors_to_details(
                serializer.errors
            )

            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                details,
                status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @override
    def update(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
        except Http404:
            # Return the same not-found shape as retrieve and delete.
            return error_response(
                "NOT_FOUND",
                "Task not found",
                [],
                status.HTTP_404_NOT_FOUND
            )

        if str(request.data.get('parent', '')) == str(instance.pk):
            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                [{
                    "field": "parent",
                    "issue": "A task cannot be a subtask of itself."
                }],
                status.HTTP_400_BAD_REQUEST
            )

        partial = kwargs.pop('partial', False)

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        if not serializer.is_valid():
            # Keep update validation errors consistent with create errors.
            details = serializer_errors_to_details(serializer.errors)

            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                details,
                status.HTTP_400_BAD_REQUEST
            )

        parent = serializer.validated_data.get('parent')
        if parent and parent.parent_id is not None:
            return error_response(
                "INVALID_OPERATION",
                "A subtask cannot have subtasks",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(serializer.data)

    @override
    def destroy(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
        except Http404:
            # Return the standard not-found response if the task is absent.
            return error_response(
                "NOT_FOUND",
                "Task not found",
                [],
                status.HTTP_404_NOT_FOUND
            )

        instance.delete()

        # HTTP 204 signals success without a response body.
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['POST'],
        url_path='from-text'
    )
    def from_text(self, request):

        text = request.data.get('text')

        if not text:
            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                [
                    {
                        "field": "text",
                        "issue": "must not be empty"
                    }
                ],
                status.HTTP_400_BAD_REQUEST
            )

        # Step 1: Parse natural language
        try:
            parsed_data = parse_task_text(
                text,
                timezone.localdate()
            )
        except Exception as e:
            logger.exception(str(e))
            return error_response(
                "PARSING_ERROR",
                "Unable to parse task text",
                [],
                status.HTTP_502_BAD_GATEWAY
            )

        # Step 2: Never trust parser output
        serializer = TaskSerializer(data=parsed_data)

        if not serializer.is_valid():
            details = serializer_errors_to_details(
                serializer.errors
            )

            return error_response(
                "VALIDATION_ERROR",
                "Parsed task validation failed",
                details,
                status.HTTP_502_BAD_GATEWAY
            )

        # Step 3: Save only after validation
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    # DRF does not allow two actions with the same method and URL path.
    # Therefore, instead of creating two separate methods named subtasks,
    # combined GET and POST in the same action.
    @action(
        detail=True,
        methods=['GET', 'POST'],
        url_path='subtasks'
    )
    def subtasks(self, request, pk=None):

        task = self.get_object()

        # A subtask cannot have its own subtasks
        if task.parent_id is not None:
            return error_response(
                "INVALID_OPERATION",
                "A subtask cannot have subtasks",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        # GET: List subtasks
        if request.method == 'GET':
            subtasks = task.subtasks.all()

            serializer = TaskSerializer(
                subtasks,
                many=True
            )

            return Response(serializer.data)

        # POST: Create subtask
        data = request.data.copy()
        if str(data.get('id', '')) == str(task.id):
            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                [{
                    "field": "id",
                    "issue": "A task cannot be a subtask of itself."
                }],
                status.HTTP_400_BAD_REQUEST
            )

        data['parent'] = task.id

        serializer = TaskSerializer(data=data)

        if not serializer.is_valid():
            details = serializer_errors_to_details(
                serializer.errors
            )

            return error_response(
                "VALIDATION_ERROR",
                "Validation failed",
                details,
                status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST'],
        url_path='breakdown'
    )
    def breakdown(self, request, pk=None):

        task = self.get_object()

        # A subtask cannot be broken down
        if task.parent_id is not None:
            return error_response(
                "INVALID_OPERATION",
                "A subtask cannot be broken down",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        # Generate subtask dictionaries
        try:
            subtasks_data = break_down_task(task)

        except Exception:
            return error_response(
                "BREAKDOWN_ERROR",
                "Unable to break down task",
                [],
                status.HTTP_502_BAD_GATEWAY
            )

        # Check whether subtasks were generated
        if not subtasks_data:
            return error_response(
                "BREAKDOWN_ERROR",
                "No subtasks generated",
                [],
                status.HTTP_502_BAD_GATEWAY
            )

        # Validate ALL subtasks before saving
        serializers = []

        for subtask_data in subtasks_data:

            serializer = TaskSerializer(data=subtask_data)

            if not serializer.is_valid():
                details = serializer_errors_to_details(
                    serializer.errors
                )

                return error_response(
                    "VALIDATION_ERROR",
                    "Subtask validation failed",
                    details,
                    status.HTTP_502_BAD_GATEWAY
                )

            serializers.append(serializer)

        # Save all subtasks inside a database transaction
        try:
            with transaction.atomic():

                created_subtasks = [
                    serializer.save()
                    for serializer in serializers
                ]

        except Exception as e:
            logger.exception(str(e))
            return error_response(
                "BREAKDOWN_ERROR",
                "Unable to save subtasks",
                [],
                status.HTTP_502_BAD_GATEWAY
            )

        # Return created subtasks
        response_serializer = TaskSerializer(
            created_subtasks,
            many=True
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
