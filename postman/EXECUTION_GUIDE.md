# Postman execution guide

## Import and run

1. Configure the PostgreSQL DB variables in .env, apply migrations, and start the server from the project root with python manage.py runserver.
2. Import Task-Management-API.postman_collection.json and Task-Management-API.postman_environment.json into Postman.
3. Select the Task Management API Local environment. Confirm base_url is http://127.0.0.1:8000 (change it if needed). Current settings do not require authentication.
4. Run the entire collection in Collection Runner in listed order. Later requests depend on IDs saved by earlier requests. Use a disposable local/test database; the suite creates persistent records.
5. Inspect the Runner Test Results tab. Open a failed request to see assertion names and response body.

The collection assigns a run_tag and captures generated IDs into environment variables. Idempotency tests require the same live Django process because the store is in-memory.

## Verify database state

Postman responses cannot prove no duplicates or transaction rollback. Use Django shell against the configured test database:

    python manage.py shell

    from tasks.models import Task
    Task.objects.filter(title__contains='QA').values('id', 'title', 'parent_id', 'priority', 'completed')
    Task.objects.filter(parent_id=<parent_id>).count()
    Task.objects.filter(title='<unique title>').count()

Check that a keyed create has one row after retry, breakdown child IDs/count stay unchanged after retry, and a deleted parent plus children are absent. For invalid requests, query by the unique run marker to confirm no row was inserted.

## Reset safely

Use a dedicated disposable database. After checking the active DB configuration, stop the server and run:

    python manage.py flush --noinput

Flush deletes every record in that database. Never use it against shared or production data. Alternatively remove only QA-marked test rows after reviewing the exact queryset and its cascade effects. Restart the server after reset; process-local idempotency state clears on restart.

## Cases needing non-Postman tests

Empty breakdown output, invalid generated subtask data, and save-time database failure cannot be forced through current HTTP inputs. Mock break_down_task / serializer saves in view tests, and assert transaction rollback. Parser call counts also require a mock or instrumentation. Postman retries assert same returned IDs; Django shell confirms actual row counts.