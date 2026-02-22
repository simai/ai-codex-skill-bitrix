# Module Contract

Apply this contract when creating or changing Bitrix modules.

## IDs and Structure

- Module ID format: `<vendor>.<code>`.
- Keep module logic under `local/modules/<vendor>.<code>/` unless repository standards require otherwise.
- Minimum structure:
  - `install/index.php`
  - `install/version.php`
  - `include.php`
  - `lib/`
  - `lang/<LANG>/...`

For admin-heavy modules, recommended extension:

- `admin/menu.php`
- `admin/<entity>_list.php`
- `admin/<entity>_edit.php`
- `options.php`
- thin proxies in `/bitrix/admin/<vendor_module>_<page>.php`

## Install / Uninstall Rules

- `DoInstall()` must validate requirements, register module, and publish required files.
- `DoUninstall()` must unregister integrations and clean runtime bindings safely.
- If module stores data, uninstall flow must support explicit retain/remove behavior.
- DB and configuration operations must be idempotent and safe on repeated runs.
- Keep install/uninstall symmetry for:
  - event handlers,
  - agents,
  - URL rewrite rules,
  - copied admin/tools/public files (when used).

Core-style implementation pattern (box source aligned):

- SQL scripts in `install/db/<db_type>/{install,uninstall}.sql`.
- Resolve DB type via application connection and execute with `RunSQLBatch(...)`.
- Register module with `RegisterModule(<module_id>)` only after successful DB stage.
- Remove module with `UnRegisterModule(<module_id>)` after cleanup stage.
- Use admin-only install/uninstall entrypoint checks (`$USER->IsAdmin()`) and `check_bitrix_sessid()`.
- For long-running background tasks, add/remove via `CAgent::AddAgent(...)` and `CAgent::RemoveModuleAgents(...)`.
- For non-trivial modules, keep two-step installer screens (`step1/step2`, `unstep1/unstep2`) and branch by `$step`.
- Validate dependencies before install side effects (feature gates, required modules, license flags).
- Isolate lifecycle code into dedicated methods (`installEventHandlers`, `uninstallEventHandlers`, `installAgents`, `uninstallAgents`) to keep symmetry explicit.
- Even with `savedata=Y`, still unregister handlers, remove agents, and detach runtime integrations.

## Admin Proxy Contract

- Real admin pages belong in module admin paths.
- `/bitrix/admin/*.php` files must be lightweight proxies, not business logic holders.
- Proxy resolution must support both local and bitrix module locations:
  1. `/local/modules/<module_id>/admin/<file>.php`
  2. fallback `/bitrix/modules/<module_id>/admin/<file>.php`
- When publishing module admin pages, follow core pattern:
  - keep proxy in `/bitrix/admin/<file>.php` as `require_once` only,
  - keep UI logic in `/local/modules/<module_id>/admin/<file>.php` or `/bitrix/modules/<module_id>/admin/<file>.php`.
- Minimal bootstrap wrappers are acceptable (prolog/module include + `require_once`), but business logic stays in module admin files.
- Build admin pages using standard APIs (`CAdminList`/`CAdminUiList`, `CAdminFilter`, `CAdminTabControl`, `CAdminContextMenu`, `CAdminMessage`) to keep compatibility with core behavior.

## Versioning and Release Metadata

- Initial version for new module: `1.0.0`.
- Update `install/version.php` on release/update tasks.
- Keep release metadata synchronized with generated release artifacts.
- `install/version.php` is the standard source for module version metadata.
- Exception note from box source: the core `main` module uses internal version constants instead of `install/version.php`.

## Data and Naming

- Table naming convention: `module_code_table_name` where `.` in module code becomes `_`.
- For import/export temporary files, prefer `/upload/tmp/<module_id>/`.
- Ensure temporary file names are unique and clean them on both success and failure paths.

## Marketplace Notes

When task explicitly targets Marketplace packaging:

- Keep partner metadata assignments explicit and static in install constructor.
- Avoid dynamic expressions for marketplace-identifying metadata fields.
