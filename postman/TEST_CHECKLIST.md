# Task API Postman test checklist

Source reviewed: tasks/models.py, tasks/serializers.py, tasks/views.py, tasks/urls.py, tasks/pagination.py, tasks/utils.py, tasks/ai.py, config/settings.py, config/urls.py. The API prefix is /api/. Authentication is not required under current DRF defaults. Error shape is custom only where views explicitly call error_response; framework exceptions may differ.

| ID | Feature | Scenario and input | Expected status / response | Database verification | Pass criteria |
|---|---|---|---|---|---|
| CRUD-01 | Create | Valid top-level task, title/description/priority/completed | 201; serialized task and generated id | Confirm one row | ID captured; fields match |
| CRUD-02 | List | GET /api/tasks/ | 200; count,next,previous,results | N/A | Paginated response keys and types match |
| CRUD-03 | Retrieve | Existing captured ID | 200; all serializer fields | N/A | ID/fields match |
| CRUD-04 | Retrieve missing | Generated missing ID | 404; NOT_FOUND custom envelope | Confirm absent | Exact error code/details structure |
| CRUD-05 | PUT | Full valid representation | 200; updated task | Verify fields | Updated values returned |
| CRUD-06 | PATCH | Partial title/completed update | 200; updated task | Verify fields | Omitted fields retained, omitted required values accepted |
| CRUD-07 | PUT vs PATCH | PUT without title/description; PATCH without them | 400 then 200 | Existing row unchanged on failure | PUT requires fields; PATCH partial accepted |
| CRUD-08 | Delete | Existing task | 204 and empty body | Verify absent | Exact 204 |
| CRUD-09 | Delete missing | Missing ID | 404 NOT_FOUND custom envelope | Confirm absent | Exact envelope |
| VAL-01 | Required fields | Missing title, missing description | 400 VALIDATION_ERROR | Confirm no row | Error details identify fields |
| VAL-02 | Blank fields | Empty and whitespace title/description | 400 VALIDATION_ERROR | Confirm no row | Custom must-not-be-empty validation |
| VAL-03 | Types | Numeric title, object description | 400 VALIDATION_ERROR | Confirm no row | Serializer rejects incompatible types |
| VAL-04 | Boolean | completed as string, number, null | 400 VALIDATION_ERROR | Confirm no row | StrictBooleanField accepts only JSON booleans |
| VAL-05 | Date | Invalid format and impossible calendar date | 400 VALIDATION_ERROR | Confirm no row | ISO YYYY-MM-DD only; invalid values rejected |
| VAL-06 | Priority | Invalid choice and null | 400 VALIDATION_ERROR | Confirm no row | Only low/medium/high supported |
| VAL-07 | Nulls | Null title/description | 400 VALIDATION_ERROR | Confirm no row | Fields are non-null |
| VAL-08 | Recurrence | Invalid value -> 400; null -> 201 | Confirm row for null case | Choice values daily/weekly/monthly/yearly; nullable |
| VAL-09 | Boundary | One-char title and description | 201 | Confirm row | Minimum nonblank values accepted |
| VAL-10 | Boundary | Title length 255 -> 201; length 256 -> 400 | Confirm only first row | Model max_length enforced |
| VAL-11 | Extra fields | Unexpected serializer key | 201; extra field absent in response | Confirm row | Current ModelSerializer ignores unrecognized input key |
| VAL-12 | Parent validation | Invalid parent id; self-parent update | 400 VALIDATION_ERROR | Confirm unchanged | Parent errors use API envelope |
| NLP-01 | from-text | Plain task text | 201 task | Confirm row | Captured task ID |
| NLP-02 | from-text | Text contains tomorrow | 201, due_date local date + 1 | Confirm date | Correct date |
| NLP-03 | from-text | Text contains every month | 201, recurrence monthly | Confirm row | Correct recurrence |
| NLP-04 | from-text | Exact date phrase such as 2030-05-20 | 201 but due_date null | Confirm row | Documents parser limitation |
| NLP-05 | from-text | Empty or missing text | 400 VALIDATION_ERROR | Confirm no row | Standard envelope |
| NLP-06 | from-text | Whitespace-only or non-string text | 502 PARSING_ERROR | Confirm no row | Parser exception caught |
| NLP-07 | from-text | Text makes generated title exceed 255 chars | 502 VALIDATION_ERROR | Confirm no row | Parsed data validated before save |
| NLP-08 | from-text | Parser exception / invalid output | HTTP can trigger whitespace/type/overlength; arbitrary output needs mock | Confirm no row | Failure does not create record |
| NLP-09a | from-text | With parser date 2026-05-01, text containing “1st” | due_date 2026-05-01 | Confirm date | If today is the first, use today |
| NLP-09b | from-text | With parser date 2026-05-20, text containing “1st” | due_date 2026-06-01 | Confirm date | Otherwise use next month’s first |
| NLP-09c | from-text | With parser date 2026-12-20, text containing “1st” | due_date 2027-01-01 | Confirm date | Year rollover works |
| SUB-01 | Subtasks | Create child under captured parent | 201; parent equals route ID | Check parent_id | Correct parent assigned |
| SUB-02 | Subtasks | Create multiple and GET list | 201 then 200 raw array | Compare child count | Both children present |
| SUB-03 | Subtasks | Missing parent | 404 DRF detail shape | Confirm no child | Framework not-found response |
| SUB-04 | Subtasks | Empty title or invalid priority | 400 VALIDATION_ERROR | Confirm no row | Validation envelope |
| SUB-05 | Subtasks | Create/list under a child | 400 INVALID_OPERATION | Confirm no nested child | Nested subtasks prohibited |
| SUB-06 | Subtasks | Delete parent and retrieve child | 204 then 404 | Confirm cascade removes both | Cascade behavior works |
| BRK-01 | Breakdown | Title with comma and 'and' | 201 array of three linked subtasks | Check all parent_id values | All split items saved |
| BRK-02 | Breakdown | Title without delimiters | 201 one child | Confirm child | Single item behavior |
| BRK-03 | Breakdown | Breakdown a subtask | 400 INVALID_OPERATION | Confirm unchanged | Rejected |
| BRK-04 | Breakdown | Missing task | 404 DRF detail shape | Confirm unchanged | Framework not-found response |
| BRK-05 | Breakdown | Empty output / invalid generated serializer values | Not directly inducible from HTTP | Mock break_down_task | Exercise 502 response |
| BRK-06 | Breakdown | Save failure after earlier save | 502 BREAKDOWN_ERROR | Inject failure; verify transaction rollback | No partial rows |
| IDEM-01 | Idempotency create | Same key and body twice | 201 twice; same task id | Count unique title = 1 | Same response ID; one database row |
| IDEM-02 | Idempotency create | Same key, different body | 422 IDEMPOTENCY_KEY_CONFLICT | No additional row | Exact error envelope |
| IDEM-03 | Idempotency create | Different key, same body | 201 twice; distinct IDs | Count = 2 | New row each time |
| IDEM-04 | Idempotency create | No key | 201 | Verify one row per call | No replay expected |
| IDEM-05 | Idempotency create | Failed then corrected with same key | 400 then 201 | One successful row | Failed response not cached |
| IDEM-06 | Idempotency from-text | Same key/body retry | 201 and same ID | Count = 1; parser call count requires instrumentation | Replay response identical resource ID |
| IDEM-07 | Idempotency breakdown | Same key/body retry | 201 and same child IDs | Child count unchanged | No duplicate children |
| IDEM-08 | Idempotency path scope | Reuse key on another endpoint/task | 422 conflict | No write | Path included in fingerprint |
| PAG-01 | Pagination | Default page size | 200; standard paginated keys | N/A | At most 10 results |
| PAG-02 | Pagination | Page 1 and page 2 | 200 with links | N/A | Links and result pages valid |
| PAG-03 | Pagination | Last page computed from count | 200 | N/A | Last-page request succeeds |
| PAG-04 | Pagination | Beyond last, page 0, negative, nonnumeric | 404 DRF detail response | N/A | Invalid page does not return 500 |
| PAG-05 | Pagination | page_size=5 | 200 | N/A | At most 5 results |
| PAG-06 | Pagination | page_size=101 | 200 | N/A | Capped at 100 |
| PAG-07 | Pagination | page_size=0 or nonnumeric | 404 DRF pagination detail | N/A | Invalid size rejected |
| FIL-01 | Filtering | completed true/false | 200 paginated results | N/A | Every result matches requested boolean |
| FIL-02 | Filtering | priority low/medium/high | 200 paginated results | N/A | Every result has requested priority |
| FIL-03 | Filtering | multiple filters and zero matches | 200 paginated response | N/A | Rows match all filters; zero match yields empty results |
| FIL-04 | Filtering | completed=maybe or completed=TRUE | 400 VALIDATION_ERROR envelope with completed details | N/A | Only lowercase true/false are accepted |
| FIL-05 | Filtering | Invalid priority choice | 400 django-filter/DRF error, not custom wrapper | N/A | 400 response |
| FIL-06 | Filtering | Empty completed value | 400 VALIDATION_ERROR envelope; empty priority value remains ignored | N/A | Supplied completed filter must be exactly true or false |
| SRCH-01 | Search | Complete/partial title and description | 200 paginated results | N/A | Matching tasks appear |
| SRCH-02 | Search | Case insensitive, no matches, empty, special chars | 200 paginated results | N/A | No-match returns empty results; no server error |
| SRCH-03 | Search | Search + filters + ordering + pagination | 200 | N/A | Combined request applies constraints |
| ORD-01 | Ordering | created_at and -created_at | 200 | N/A | Current page sorted ascending/descending |
| ORD-02 | Ordering | Ordering with filter and search | 200 | N/A | Query accepted with matches |
| ORD-03 | Ordering | Invalid/empty ordering | 200 | N/A | Invalid field ignored; default is -created_at |
| PRI-01 | Priority action | low/medium/high | 200 paginated result | N/A | Results all match requested level |
| PRI-02 | Priority action | urgent or uppercase HIGH | 400 INVALID_PRIORITY custom envelope | N/A | Exact error code and details |
| PRI-03 | Priority action | Empty matching records and page size | 200 paginated response | N/A | Empty results and links/count correct |
| COM-01 | Combined | completed=false and priority=high | 200 | N/A | Every result satisfies both |
| COM-02 | Combined | Search plus newest ordering | 200 | N/A | Search results sorted newest first |
| COM-03 | Combined | Update then query filter | 200 | Confirm row updated | Updated task appears in result |

## Implementation gaps / risks

- parse_task_text recognizes only 'tomorrow', 'every month', and substring '1st'. Specific calendar dates are not parsed. For '1st', it uses today when today is the first; otherwise it selects the first of the next month, including rolling December into January.
- Idempotency uses a process-local, unbounded dictionary. It is lost on restart, not shared across workers, has no expiration/locking, and concurrent same-key requests can race.
- Some errors are custom envelopes, but get_object failures in subtask/breakdown, pagination errors, and django-filter errors use DRF/framework shapes.
- The completed list filter now accepts exactly the lowercase query values true and false; all other supplied values return a VALIDATION_ERROR envelope before django-filter runs.
- Subtask listing is an unpaginated raw array. CRUD list and priority action are paginated.
- Postman cannot prove database rollback, no row creation, parser invocation count, or true duplicate count; use database queries or mocked view tests.
