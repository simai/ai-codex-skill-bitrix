# Bitrix24 REST Domain Pack: User

Use this pack for user directory sync, employee lifecycle, and identity mapping.

Base references:

- `references/bitrix24-rest-integration.md`
- `references/bitrix24-rest-docs-triage.md`
- `references/bitrix24-rest-event-lifecycle.md`

Delivery artifact template:

- `references/template-rest-domain-user-artifact-pack.md`

## 1) Source Triage

Tier A (primary):

- `<b24-rest-docs-root>/api-reference/user/index.md`
- `<b24-rest-docs-root>/api-reference/user/user-get.md`
- `<b24-rest-docs-root>/api-reference/user/user-search.md`
- `<b24-rest-docs-root>/api-reference/user/user-current.md`
- `<b24-rest-docs-root>/api-reference/user/user-fields.md`
- `<b24-rest-docs-root>/api-reference/user/user-add.md`
- `<b24-rest-docs-root>/api-reference/user/user-update.md`
- `<b24-rest-docs-root>/api-reference/user/user-scope.md`

Tier B (use with runtime validation):

- `<b24-rest-docs-root>/api-reference/user/userfields/user-userfield-file-get.md` (in-progress markers)

Tier C (none critical in core branch; treat unknown old snippets as non-authoritative).

## 2) Integration Contract

Scope and data access rules:

- Choose minimum required user scope:
  - `user_brief` for non-contact display,
  - `user_basic` for basic contact data,
  - `user` for full profile and management methods.
- Field visibility depends on granted scope; implement safe fallback for missing fields.

Read rules:

- Use `user.get` for structured filtering and pagination.
- Use `user.search` for fast fulltext-style user discovery.
- In `user.search`, do not mix `FIND` with other filter fields in one request.

Write rules:

- `user.add` and `user.update` require admin-level context.
- Intranet invite requires `UF_DEPARTMENT`.
- Extranet invite requires `EXTRANET=Y` plus `SONET_GROUP_ID`.
- Treat user activation/deactivation (`ACTIVE`) as stateful HR event and log actor/time.

Security and privacy:

- Avoid storing unneeded personal fields.
- Mask sensitive user details in logs and incident reports.
- Restrict use of `ADMIN_MODE` to controlled service paths only.

## 3) Starter Templates

Template A: scope profile (`yaml`)

```yaml
domain: user
scope_mode: user_basic
required_methods:
  - user.get
  - user.search
  - user.current
optional_admin_methods:
  - user.add
  - user.update
privacy:
  log_mask_fields:
    - EMAIL
    - PERSONAL_PHONE
    - PERSONAL_MOBILE
```

Template B: directory sync filter (`json`)

```json
{
  "SORT": "ID",
  "ORDER": "ASC",
  "FILTER": {
    "ACTIVE": true,
    "USER_TYPE": "employee"
  },
  "start": 0
}
```

Template C: controlled invite payload (`json`)

```json
{
  "EMAIL": "new.employee@example.com",
  "UF_DEPARTMENT": [1],
  "NAME": "Alex",
  "LAST_NAME": "Ivanov"
}
```

## 4) QA Gate (User)

Mandatory checks:

- Scope is minimal and justified (`user_brief`/`user_basic`/`user`).
- Behavior with reduced scope is tested (missing fields do not break flow).
- `user.search` filter contract is respected (`FIND` exclusivity).
- `user.add`/`user.update` are protected by admin-only execution path.
- PII masking is present in logs and reports.

Evidence commands:

```bash
rg -n "user\\.(get|search|current|add|update|fields)|ADMIN_MODE|UF_DEPARTMENT|EXTRANET|SONET_GROUP_ID" <project_root>
```

```bash
rg -n "EMAIL|PERSONAL_PHONE|PERSONAL_MOBILE" <project_root> | rg -v "mask|redact|hash"
```
