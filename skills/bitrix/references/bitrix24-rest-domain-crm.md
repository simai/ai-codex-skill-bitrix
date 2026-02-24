# Bitrix24 REST Domain Pack: CRM

Use this pack for CRM integrations after applying:

- `references/bitrix24-rest-integration.md`
- `references/bitrix24-rest-docs-triage.md`
- `references/bitrix24-rest-event-lifecycle.md`

Delivery artifact template:

- `references/template-rest-domain-crm-artifact-pack.md`

## 1) Source Triage

Tier A (primary for new integrations):

- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-list.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-get.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-add.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-update.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-delete.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/crm-item-fields.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/object-fields.md`

Tier B (use only with runtime checks):

- `<b24-rest-docs-root>/api-reference/crm/index.md`
- `<b24-rest-docs-root>/api-reference/crm/universal/index.md`
- `<b24-rest-docs-root>/api-reference/crm/data-types.md`
- pages marked with `Мы еще обновляем эту страницу` or `TO-DO _не выгружается на prod_`

Tier C (compatibility-only, not default for new builds):

- `<b24-rest-docs-root>/api-reference/crm/outdated/**`
- classic entity methods where docs contain `Развитие метода остановлено` (`crm.deal.*`, `crm.lead.*`, `crm.contact.*`, `crm.company.*` in old branches)

## 2) Integration Contract

Primary rules:

- For new development, use `crm.item.*` as default API surface.
- Treat `entityTypeId` as required routing key for every operation.
- Build field schema from `crm.item.fields` per `entityTypeId`, cache per portal, and refresh on reinstall/update.
- Set `useOriginalUfNames` explicitly (`Y` or `N`) and keep one format project-wide.

Read/write rules:

- Always send explicit `select` in `crm.item.list` / `crm.item.get`.
- Use `start` pagination (`50` rows per page) with deterministic ordering.
- In `crm.item.update`, send only changed fields.
- Validate payload before call; docs indicate unknown fields can be ignored silently.

Reliability rules:

- Expect side effects on write calls (required fields checks, automation/robots).
- Define idempotency key strategy for inbound/outbound sync (`portal + entityTypeId + externalId`).
- Use bounded retries for transient errors and rate limits.

Compatibility rules:

- If portal lacks required `crm.item.*` capability, fallback to legacy methods only behind explicit compatibility branch and risk note.

## 3) Starter Templates

Template A: capability requirements (`yaml`)

```yaml
domain: crm
required_scope:
  - crm
required_methods:
  - crm.item.list
  - crm.item.get
  - crm.item.add
  - crm.item.update
  - crm.item.delete
  - crm.item.fields
entity_types:
  - 1   # lead
  - 2   # deal
  - 3   # contact
  - 4   # company
```

Template B: pull-sync loop (`pseudo`)

```text
for each entityTypeId in sync scope:
  refresh field map with crm.item.fields(entityTypeId)
  page = 0
  do:
    start = page * 50
    rows = crm.item.list(entityTypeId, select, filter, order, start)
    upsert rows with idempotency key (portal, entityTypeId, id, updatedTime)
    page++
  while rows not empty
```

Template C: outbound upsert payload (`json`)

```json
{
  "entityTypeId": 2,
  "id": 12345,
  "fields": {
    "title": "Deal from external system",
    "opportunity": 15000,
    "currencyId": "USD",
    "originatorId": "ext.crm",
    "originId": "deal-88421"
  },
  "useOriginalUfNames": "N"
}
```

## 4) QA Gate (CRM)

Mandatory checks:

- `crm.item.fields` schema cache exists and refreshes on lifecycle events.
- `entityTypeId` mapping is explicit and covered by tests.
- List pagination completeness validated (no missed/duplicated rows across pages).
- Field-name format (`useOriginalUfNames`) is consistent across read and write paths.
- Legacy fallback (if present) is feature-flagged and documented.

Evidence commands:

```bash
rg -n "crm\\.item\\.(list|get|add|update|delete|fields)|entityTypeId|useOriginalUfNames" <project_root>
```

```bash
rg -n "crm\\.(deal|lead|contact|company)\\." <project_root>
```
