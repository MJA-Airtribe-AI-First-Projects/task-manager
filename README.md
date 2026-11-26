# 📝 Task Manager — Task Management API

> A Django REST Framework API for managing tasks, creating tasks using natural language, and automatically breaking down complex tasks into smaller subtasks.

Task Manager is a backend application built using Python, Django, and Django REST Framework. It provides RESTful APIs to create, retrieve, update, and delete tasks, along with advanced capabilities such as natural-language task creation, automatic task breakdown, and parent-child task relationships.

The application focuses on clean API design, reusable serializers, custom validation, error handling, database transactions, and idempotent request handling to ensure reliable API operations.

---

## ✨ Features

- 📋 **Task CRUD Operations** — Create, retrieve, update, and delete tasks.
- 🔍 **Task Listing & Filtering** — Retrieve tasks with filtering and pagination support.
- 🧠 **Natural Language Task Creation** — Create tasks by providing a natural-language description.
- 🧩 **Automatic Task Breakdown** — Break down complex tasks into smaller, manageable subtasks.
- 🔗 **Parent-Child Relationships** — Maintain relationships between parent tasks and their subtasks.
- ✅ **Custom Validation** — Validate incoming request data using DRF serializers.
- ⚠️ **Error Handling** — Handle invalid input, missing resources, and business logic errors.
- 🔄 **Idempotent API Requests** — Prevent duplicate task creation when clients retry requests.
- 🔒 **Atomic Database Transactions** — Ensure database consistency during operations involving multiple records.
- 🧪 **API Testing** — Test successful and unsuccessful scenarios using Postman.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Django | Backend web framework |
| Django REST Framework | REST API development |
| Django ORM | Database models and queries |
| SQLite | Database for local development |
| Postman | API testing |
| Git & GitHub | Version control and source code management |

---

# 🚀 Getting Started

Follow the steps below to set up and run the project locally.

## 1. Clone the repository

Open PowerShell or Command Prompt:

```bash
git clone https://github.com/MJA-Airtribe-AI-First-Projects/task-manager.git

cd task-manager
```

## 2. Create and activate a virtual environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## 3. Install dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

## 4. Apply database migrations

Generate migrations if required:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

## 5. Run the development server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

The API endpoints are available under:

```text
http://127.0.0.1:8000/api/
```

---

# 📁 Project Structure

```text
task-manager/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── tasks/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── requirements.txt
└── README.md
```

| Component | Responsibility |
|---|---|
| `config/` | Django project configuration and root URL routing |
| `tasks/models.py` | Task and subtask database models |
| `tasks/serializers.py` | Serialization, validation, and data handling |
| `tasks/views.py` | API endpoints and business logic |
| `tasks/urls.py` | Task API URL configuration |
| `tasks/migrations/` | Database schema migrations |
| `requirements.txt` | Project dependencies |
| `manage.py` | Django management commands |

---

# 🧱 Data Models

## 1. Task

The `Task` model stores both top-level tasks and subtasks. Django adds an automatic primary key, exposed by the API as `id`.

| Field | Django type | Details |
|---|---|---|
| `id` | Automatic primary key | Added by Django; uniquely identifies each task. |
| `title` | `CharField` | Required and non-null; maximum length is 255 characters. Whitespace-only values are rejected by serializer validation. |
| `description` | `TextField` | Required and non-null. Whitespace-only values are rejected by serializer validation. |
| `completed` | `BooleanField` | Defaults to `false`. The API requires JSON boolean values when supplied. |
| `due_date` | `DateField` | Optional and nullable; the API accepts `YYYY-MM-DD` or `null`. |
| `priority` | `CharField` | Maximum length 10; choices are `low`, `medium`, and `high`; defaults to `medium`. |
| `parent` | Self-referencing `ForeignKey` | Optional and nullable; points to another `Task`. Deleting a parent cascades to its subtasks. The reverse relation is named `subtasks`. |
| `created_at` | `DateTimeField` | Automatically set when the task is created. |
| `updated_at` | `DateTimeField` | Automatically refreshed whenever the task is saved. |
| `recurrence` | `CharField` | Optional and nullable; maximum length 20; choices are `daily`, `weekly`, `monthly`, and `yearly`. |

### Parent and subtask relationship

There is no separate `Subtask` model. A subtask is a `Task` whose `parent` field points to another task; top-level tasks have `parent` set to `null`. The reverse relation on a parent is available as `task.subtasks`.

---

# 🔌 API Endpoints

All endpoints accept and return JSON.

Base URL:

```text
http://127.0.0.1:8000/api/
```

## 📋 Task APIs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tasks/` | Retrieve all tasks |
| `POST` | `/api/tasks/` | Create a new task |
| `GET` | `/api/tasks/<id>/` | Retrieve a specific task |
| `PUT` | `/api/tasks/<id>/` | Update an existing task |
| `PATCH` | `/api/tasks/<id>/` | Partially update a task |
| `DELETE` | `/api/tasks/<id>/` | Delete a task |
| `POST` | `/api/tasks/from-text/` | Create a task using natural language |

### Create a Task

**POST**

```text
/api/tasks/
```

Example request:

```json
{
    "title": "Build Task Manager API",
    "description": "Implement task CRUD operations",
    "completed": false,
    "user": 1
}
```

A successful request returns `201 Created` with the newly created task.

### Retrieve Tasks

**GET**

```text
/api/tasks/
```

The API supports paginated task responses.

Example response structure:

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Build Task Manager API",
            "description": "Implement task CRUD operations",
            "completed": false,
            "created_at": "2026-11-20T10:00:00Z",
            "updated_at": "2026-11-20T10:00:00Z"
        }
    ]
}
```

### Retrieve a Specific Task

**GET**

```text
/api/tasks/1/
```

Returns the details of the requested task.

### Update a Task

**PUT**

```text
/api/tasks/1/
```

Updates the existing task.

### Partially Update a Task

**PATCH**

```text
/api/tasks/1/
```

Example request:

```json
{
    "completed": true
}
```

### Delete a Task

**DELETE**

```text
/api/tasks/1/
```

Deletes the specified task.

---

## 🧠 Natural Language Task Creation

The application supports creating tasks using natural-language input.

Instead of manually providing individual task fields, users can describe their requirements in plain text.

**POST**

```text
/api/tasks/from-text/
```

The API processes the natural-language input using a rule-based parsing mechanism and extracts the relevant task information before creating the task.

This feature demonstrates how natural-language processing concepts can be integrated into a traditional REST API workflow.

---

## 🧩 Subtask APIs

Subtasks allow users to divide complex tasks into smaller, manageable units.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tasks/<id>/subtasks/` | Create a subtask |
| `GET` | `/api/tasks/<id>/subtasks/` | Retrieve subtasks associated with a task |

### Create a Subtask

**POST**

```text
/api/tasks/1/subtasks/
```

Creates a subtask associated with the specified parent task.

A successful request returns `201 Created`.

### Retrieve Subtasks

**GET**

```text
/api/tasks/1/subtasks/
```

Returns the list of subtasks belonging to the specified parent task.

---

## 🔄 Automatic Task Breakdown

The application provides an automatic task breakdown feature that converts a complex task into multiple smaller subtasks.

**POST**

```text
/api/tasks/1/breakdown/
```

The breakdown operation:

1. Retrieves the parent task.
2. Calls `break_down_task(task)` to generate a list of subtask dictionaries.
3. Creates the generated subtasks in the database.
4. Associates each subtask with its parent task.
5. Returns the created subtasks.

### Database Transaction Handling

The breakdown operation uses Django database transactions to maintain data consistency.

The operation is performed atomically so that either all subtasks are created successfully or none of the changes are committed.

This prevents partially created subtasks if an error occurs during the operation.

---

# 🔁 Idempotency Support

Network failures and client retries can result in duplicate API requests.

To prevent duplicate resource creation, the application supports an optional `Idempotency-Key` HTTP header.

### Supported Endpoints

| Method | Endpoint |
|---|---|
| `POST` | `/api/tasks/` |
| `POST` | `/api/tasks/from-text/` |
| `POST` | `/api/tasks/<id>/breakdown/` |

### How It Works

The client sends an `Idempotency-Key` header with the request.

Example:

```http
Idempotency-Key: task-create-123
```

The application maintains an in-memory dictionary containing the request body and its corresponding response.

The following scenarios are handled:

| Scenario | Expected Behaviour |
|---|---|
| Same key + same request body | Returns the previously stored response |
| Same key + different request body | Rejects the request |
| New idempotency key | Processes the request normally |
| Request without an idempotency key | Processes the request normally |

This ensures that retrying an API request with the same key and payload does not create duplicate resources.

**Note:** The current implementation uses an in-memory dictionary. Idempotency records are therefore not persistent across server restarts and are not shared across multiple application processes.

For production systems, a persistent shared store such as Redis or a database-backed implementation would be more appropriate.

---

# 🧠 Design Decisions

## 1. Why use Django REST Framework serializers?

Serializers provide a centralized mechanism for converting model instances into JSON-compatible representations and validating incoming request data.

This keeps validation logic organized and reduces duplication across API endpoints.

## 2. Why use ViewSets and custom actions?

ViewSets help organize related CRUD operations into a single class.

Custom actions using `@action` allow additional business operations, such as:

- Creating subtasks.
- Retrieving subtasks.
- Breaking down a complex task.

This keeps the API structure clean and REST-oriented.

## 3. Why use database transactions for task breakdown?

Task breakdown involves creating multiple related database records.

Without transaction management, an error during subtask creation could leave the database in an inconsistent state.

Using `transaction.atomic()` ensures that all database changes succeed together or are rolled back together.

## 4. Why implement idempotency?

HTTP requests can fail due to network interruptions even when the server has successfully processed them.

When clients retry such requests, duplicate resources can be created.

Idempotency ensures that repeated requests with the same key and payload reuse the original response instead of repeating the operation.

## 5. Why use a rule-based parser?

A rule-based parser provides a predictable way to extract task information from natural-language input.

It also allows the parsing logic to be maintained independently of the API views.

---

# 🧪 Testing with Postman

Postman can be used to test all Task Manager API endpoints.

Start the Django development server:

```bash
python manage.py runserver
```

### Recommended Testing Workflow

1. Create a task — `POST /api/tasks/`
2. Retrieve all tasks — `GET /api/tasks/`
3. Retrieve a specific task — `GET /api/tasks/<id>/`
4. Update a task — `PUT /api/tasks/<id>/`
5. Partially update a task — `PATCH /api/tasks/<id>/`
6. Delete a task — `DELETE /api/tasks/<id>/`
7. Create a task using natural language — `POST /api/tasks/from-text/`
8. Create a subtask — `POST /api/tasks/<id>/subtasks/`
9. Retrieve subtasks — `GET /api/tasks/<id>/subtasks/`
10. Break down a task — `POST /api/tasks/<id>/breakdown/`
11. Test idempotency using the same key and request body.
12. Test idempotency using the same key with a different request body.
13. Test requests with missing or invalid fields.
14. Test requests for non-existing task IDs.
15. Verify transaction rollback when task breakdown fails.

### Important Test Scenarios

| Scenario | Expected Result |
|---|---|
| Create a task with valid data | `201 Created` |
| Retrieve an existing task | `200 OK` |
| Update an existing task | `200 OK` |
| Delete an existing task | `204 No Content` |
| Submit invalid task data | `400 Bad Request` |
| Retrieve a non-existing task | `404 Not Found` |
| Create a subtask with valid data | `201 Created` |
| Break down an existing task | Successful subtask creation |
| Repeat a request with the same idempotency key and body | Previously stored response |
| Reuse an idempotency key with a different body | Conflict/error response |
| Trigger an error during breakdown | Database changes rolled back |

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of several backend development concepts:

- Django models and ORM relationships.
- Django REST Framework serializers and ViewSets.
- RESTful API design and routing.
- Custom serializer validation.
- Reusable business logic.
- Natural-language parsing.
- Parent-child database relationships.
- Atomic database transactions.
- Idempotent API design.
- API testing and error handling.

The project was developed as part of the **Airtribe AI-First Projects** learning journey, with a focus on strengthening backend development skills through practical implementation.
