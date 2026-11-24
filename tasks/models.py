from django.db import models


class Task(models.Model):
    # Allowed priority values and their human-readable labels.
    PRIORITY_CHOICES = (('low', 'Low'),
                        ('medium', 'Medium'),
                        ('high', 'High'))
    RECURRENCE_CHOICES = (('daily', 'Daily'),
                          ('weekly', 'Weekly'),
                          ('monthly', 'Monthly'),
                          ('yearly', 'Yearly'))

    # Short name shown for the task.
    title = models.CharField(max_length=255, blank=False, null=False)
    # Longer details about what needs to be done.
    description = models.TextField(blank=False, null=False)
    # Whether the task has been completed; new tasks start incomplete.
    completed = models.BooleanField(default=False)
    # Optional deadline. `dueDate` can be left empty or set to NULL.
    due_date = models.DateField(null=True, blank=True)
    # Task priority, restricted to the values in PRIORITY_CHOICES.
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    # Optional parent task; a task can have child tasks through `subtasks`.
    parent = models.ForeignKey('self', related_name='subtasks', on_delete=models.CASCADE, default=None, null=True,
                               blank=True)
    # Set automatically when the task is first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Refreshed automatically whenever the task is saved.
    updated_at = models.DateTimeField(auto_now=True)
    # Optional schedule interval for repeating this task.
    recurrence = models.CharField(max_length=20, null=True, blank=True, choices=RECURRENCE_CHOICES)

    def __str__(self):
        # Use the task title when displaying this object.
        return self.title

    class Meta:
        # Store task records in the database table named `tasks`.
        db_table = 'tasks'
