import re
from datetime import date, timedelta


def parse_task_text(text, today):
    """
    Convert natural-language task text into structured task data.

    Args:
        text (str): Natural-language task description.
        today (date): Current date.

    Returns:
        dict: title, description, due_date and optional recurrence.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text_lower = text.lower()

    due_date = None
    recurrence = None

    # Handle tomorrow
    if "tomorrow" in text_lower:
        print(today)
        due_date = today + timedelta(days=1)

    # Handle every month
    if "every month" in text_lower:
        recurrence = "monthly"

    # Handle 1st
    if "1st" in text_lower:

        if today.day < 1:
            due_date = today.replace(day=1)

        else:
            # First day of next month
            if today.month == 12:
                due_date = date(today.year + 1, 1, 1)
            else:
                due_date = date(today.year, today.month + 1, 1)

    # Basic title and description extraction
    title = text.strip()

    description = text.strip()

    result = {
        "title": title,
        "description": description,
        "due_date": due_date.isoformat() if due_date else None
    }

    if recurrence:
        result["recurrence"] = recurrence

    return result


def break_down_task(task):
    return [
        {
            "title": "Create Serializer",
            "description": "Create serializer",
            "parent": task.id
        },
        {
            "title": "",
            "description": "Invalid subtask",
            "parent": task.id
        }
    ]
    title = task.title

    # Split using 'and' or commas
    subtasks = re.split(r'\s+and\s+|,\s*', title, flags=re.IGNORECASE)

    subtasks = [
        item.strip()
        for item in subtasks
        if item.strip()
    ]

    result = []

    for item in subtasks:
        result.append({
            "title": item,
            "description": item,
            "parent": task.id
        })

    return result
