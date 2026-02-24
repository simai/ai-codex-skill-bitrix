# Bitrix24 REST Domain Pack: Disk

Use this pack for file upload pipelines, folder/file lifecycle, and permissions-aware storage integration.

Base references:

- `references/bitrix24-rest-integration.md`
- `references/bitrix24-rest-docs-triage.md`
- `references/bitrix24-rest-event-lifecycle.md`
- `<b24-rest-docs-root>/api-reference/files/how-to-upload-files.md`

Delivery artifact template:

- `references/template-rest-domain-disk-artifact-pack.md`

## 1) Source Triage

Tier A (primary):

- `<b24-rest-docs-root>/api-reference/disk/index.md`
- `<b24-rest-docs-root>/api-reference/disk/storage/disk-storage-get-list.md`
- `<b24-rest-docs-root>/api-reference/disk/storage/disk-storage-get-children.md`
- `<b24-rest-docs-root>/api-reference/disk/storage/disk-storage-upload-file.md`
- `<b24-rest-docs-root>/api-reference/disk/folder/disk-folder-get-children.md`
- `<b24-rest-docs-root>/api-reference/disk/folder/disk-folder-upload-file.md`
- `<b24-rest-docs-root>/api-reference/disk/file/disk-file-get.md`
- `<b24-rest-docs-root>/api-reference/disk/file/disk-file-mark-deleted.md`
- `<b24-rest-docs-root>/api-reference/disk/file/disk-file-delete.md`
- `<b24-rest-docs-root>/api-reference/disk/rights/disk-rights-get-tasks.md`

Tier B (no critical in-progress markers in core file/storage/folder branch at time of extraction).

Tier C (none mandatory; treat unknown old snippets as compatibility-only).

## 2) Integration Contract

Discovery and navigation:

- Resolve object IDs through `disk.storage.getlist` -> `disk.storage.getchildren` / `disk.folder.getchildren`.
- Use explicit filters/order and `start` pagination (`50` rows/page).

Upload strategy:

- Direct upload: pass `data.NAME` + `fileContent=[name, base64]`.
- Deferred upload: call `disk.folder.uploadfile` without `fileContent` to get `uploadUrl` and form field.
- Set `generateUniqueName` explicitly when name collision is possible.

Permissions and sharing:

- Use `disk.rights.getTasks` to obtain valid `TASK_ID` values.
- Set `rights` with strict `ACCESS_CODE` validation (`U`, `D`, `DR`, `*` forms).
- Verify resulting access via read attempts from expected roles/users.

Delete policy:

- Default to soft delete via `disk.file.markdeleted`.
- Use hard delete (`disk.file.delete`) only in explicit cleanup flows.
- Keep file IDs for restore and audit after soft-delete operations.

Reliability and safety:

- Handle lock/conflict responses (e.g., exclusive lock) with bounded retry.
- Keep large transfer workers queue-based and idempotent.
- Never log raw file payload/base64 blobs.

## 3) Starter Templates

Template A: upload policy (`yaml`)

```yaml
domain: disk
upload_mode: direct_base64
collision_policy: generate_unique_name
delete_policy: soft_delete
required_methods:
  - disk.storage.getlist
  - disk.storage.getchildren
  - disk.folder.getchildren
  - disk.folder.uploadfile
  - disk.file.get
  - disk.file.markdeleted
optional_methods:
  - disk.file.delete
  - disk.rights.getTasks
```

Template B: upload request (`json`)

```json
{
  "id": 8930,
  "data": { "NAME": "contract.pdf" },
  "fileContent": ["contract.pdf", "<base64>"],
  "generateUniqueName": true
}
```

Template C: safe delete workflow (`pseudo`)

```text
if policy == soft:
  disk.file.markdeleted(id)
  store (portal, fileId, deletedAt, actor)
else if policy == hard:
  verify ownership/rights
  disk.file.delete(id)
  store deletion audit entry
```

## 4) QA Gate (Disk)

Mandatory checks:

- Upload works in both direct and URL-based flow where required.
- `generateUniqueName` behavior is tested on duplicate names.
- Permission assignment via `rights` is validated for intended users/roles.
- Soft delete + restore scenario is validated before enabling hard delete flows.
- Lock/conflict handling is verified under concurrent edit/upload simulation.

Evidence commands:

```bash
rg -n "disk\\.(storage|folder|file|rights)\\.|generateUniqueName|fileContent|markdeleted|delete" <project_root>
```

```bash
rg -n "base64|fileContent" <project_root> | rg -v "mask|redact|truncate"
```
