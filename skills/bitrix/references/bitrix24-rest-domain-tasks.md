# Bitrix24 REST Domain Pack: Tasks

Use this pack for task lifecycle, assignment, and task-sync integrations.

Base references:

- `references/bitrix24-rest-integration.md`
- `references/bitrix24-rest-docs-triage.md`
- `references/bitrix24-rest-event-lifecycle.md`

Delivery artifact template:

- `references/template-rest-domain-tasks-artifact-pack.md`

## 1) Source Triage

Tier A (primary):

- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-list.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-get.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-add.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-update.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-delete.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-get-fields.md`
- `<b24-rest-docs-root>/api-reference/tasks/tasks-task-history-list.md`

Tier B (use with runtime validation):

- `<b24-rest-docs-root>/api-reference/tasks/fields.md` (page is marked as in-progress)
- `<b24-rest-docs-root>/api-reference/tasks/user-field/**` (pages with in-progress markers)
- `<b24-rest-docs-root>/api-reference/tasks/comment-item/*.md` (methods marked stopped in newer module versions)

Tier C (do not use as default for new flows):

- `<b24-rest-docs-root>/api-reference/tasks/deprecated/**`
- legacy `task.item.*` compatibility layer only

## 2) Integration Contract

Primary rules:

- Use `tasks.task.*` methods for all new integrations.
- Use `tasks.task.getFields` as runtime schema source; do not hardcode from docs pages.
- Build explicit `select` lists in `tasks.task.list` and `tasks.task.get`.

Lifecycle rules:

- Create: require `TITLE`, `RESPONSIBLE_ID`, and portal-required custom fields.
- Update: require at least one changed field; send only changed fields.
- Delete: use `tasks.task.delete` only after access check (e.g., via `tasks.task.getaccess`).

Field-specific rules:

- For CRM bindings use `UF_CRM_TASK` with strict value format (`L_`, `D_`, `C_`, `CO_`).
- For file attachments use `UF_TASK_WEBDAV_FILES` values as disk IDs with `n` prefix.
- For status transitions, prefer action methods (`tasks.task.start`, `pause`, `defer`, etc.) over implicit state mutations when possible.

Pagination and scale:

- `tasks.task.list` and history endpoints use `start` pagination with fixed page size 50.
- Use chunked readers and bounded parallelism on large datasets.

## 3) Starter Templates

Template A: required-method profile (`yaml`)

```yaml
domain: tasks
required_scope:
  - task
required_methods:
  - tasks.task.list
  - tasks.task.get
  - tasks.task.add
  - tasks.task.update
  - tasks.task.delete
  - tasks.task.getFields
  - tasks.task.history.list
optional_methods:
  - tasks.task.getaccess
  - tasks.task.start
  - tasks.task.pause
  - tasks.task.defer
```

Template B: create payload baseline (`json`)

```json
{
  "fields": {
    "TITLE": "Prepare monthly report",
    "RESPONSIBLE_ID": 25,
    "DEADLINE": "2026-03-01T18:00:00",
    "UF_CRM_TASK": ["D_1205"],
    "UF_TASK_WEBDAV_FILES": ["n32895"]
  }
}
```

Template C: incremental sync loop (`pseudo`)

```text
fields = tasks.task.getFields()
page = 0
do:
  start = page * 50
  rows = tasks.task.list(select, filter, order, start)
  normalize using runtime fields map
  upsert by (portal, taskId, changedDate)
  page++
while rows not empty
```

## 4) QA Gate (Tasks)

Mandatory checks:

- No use of `tasks/deprecated/*` methods in production path.
- `select` is explicit in list/get calls and includes needed UF fields.
- Required custom fields are discovered and validated before create/update.
- Access checks exist before delete/state-changing operations.
- Attachment format (`UF_TASK_WEBDAV_FILES`) and CRM bindings (`UF_CRM_TASK`) are validated.

Evidence commands:

```bash
rg -n "tasks\\.task\\.(list|get|add|update|delete|getFields|history\\.list)|UF_CRM_TASK|UF_TASK_WEBDAV_FILES" <project_root>
```

```bash
rg -n "task\\.item\\.|tasks/deprecated" <project_root>
```
