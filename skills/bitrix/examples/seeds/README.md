# Large Dataset Seeds (UX/Performance)

This folder provides reusable datasets for list/filter/pagination load checks.

## Files

- `mysql_large_list_seed.sql`: creates table `qa_employees_perf` and inserts 100000 rows.
- `mysql_large_list_cleanup.sql`: drops `qa_employees_perf`.
- `seed_iblock_employees.php`: inserts elements into a target IBlock.
- `seed_hlblock_employees.php`: inserts rows into a target HLBlock.

## 1) SQL seed for custom/module table

```bash
mysql -u root -p your_db < skills/bitrix/examples/seeds/mysql_large_list_seed.sql
```

Cleanup:

```bash
mysql -u root -p your_db < skills/bitrix/examples/seeds/mysql_large_list_cleanup.sql
```

## 2) IBlock seed (CLI)

```bash
BITRIX_ROOT="/absolute/path/to/site" \
IBLOCK_ID=10 \
SEED_COUNT=50000 \
SEED_CHUNK=1000 \
php skills/bitrix/examples/seeds/seed_iblock_employees.php
```

Optional env:

- `IBLOCK_SECTION_ID` (default `0`, no section)
- `SEED_START_FROM` (default `1`, useful for reruns)

## 3) HLBlock seed (CLI)

```bash
BITRIX_ROOT="/absolute/path/to/site" \
HLBLOCK_ID=12 \
SEED_COUNT=50000 \
SEED_CHUNK=1000 \
php skills/bitrix/examples/seeds/seed_hlblock_employees.php
```

Optional env:

- `SEED_START_FROM` (default `1`)
- `HL_TITLE_FIELD` (default `UF_NAME`)
- `HL_CODE_FIELD` (default `UF_XML_ID`)
- `HL_ACTIVE_FIELD` (default `UF_ACTIVE`)
- `HL_SORT_FIELD` (default `UF_SORT`)

## Notes

- Use on stage/test only.
- Large inserts can take time and disk space.
- Reindex caches/search as required by project policy after large inserts.
