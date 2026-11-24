from rest_framework import serializers

from .models import Task


class StrictBooleanField(serializers.BooleanField):

    def to_internal_value(self, data):
        # Reject strings and numbers instead of coercing them to booleans.
        if not isinstance(data, bool):
            raise serializers.ValidationError(
                "must be a boolean"
            )

        return super().to_internal_value(data)


class TaskSerializer(serializers.ModelSerializer):
    # Allow blank input through so the validators can return the API's message.
    title = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    # Omitted values default to false; supplied values must still be booleans.
    completed = StrictBooleanField(required=False, default=False)
    # Accept ISO calendar dates and allow the deadline to be omitted or null.
    due_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Task
        fields = '__all__'
        # These values are managed by the database or model lifecycle.
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_parent(self, value):
        if self.instance and value and value.pk == self.instance.pk:
            raise serializers.ValidationError(
                "A task cannot be a subtask of itself."
            )
        return value

    def validate_title(self, value):
        # `strip` catches strings containing only whitespace.
        if not value.strip():
            raise serializers.ValidationError(
                "must not be empty."
            )
        return value

    def validate_description(self, value):
        # Treat whitespace-only descriptions as empty.
        if not value.strip():
            raise serializers.ValidationError(
                "must not be empty."
            )
        return value
