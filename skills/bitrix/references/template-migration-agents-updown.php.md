# Template: Migration `up/down` for Agents

Use this template to add/remove module agents safely and idempotently.

```php
<?php

use Bitrix\Main\Loader;

final class UpdateEmployeeAgentsMigration
{
	private const MODULE_ID = 'vendor.module';
	private const AGENT_NAME = '\\Vendor\\Module\\Agent\\EmployeeSyncAgent::run();';
	private const AGENT_INTERVAL = 300; // seconds

	public function up(): void
	{
		if (!Loader::includeModule('main'))
		{
			throw new \RuntimeException('Module main is not available.');
		}

		$this->removeAgentIfExists();

		$agentId = \CAgent::AddAgent(
			self::AGENT_NAME,
			self::MODULE_ID,
			'N',
			self::AGENT_INTERVAL,
			'',
			'Y',
			'',
			100
		);

		if ((int)$agentId <= 0)
		{
			throw new \RuntimeException('Unable to add agent: ' . self::AGENT_NAME);
		}
	}

	public function down(): void
	{
		if (!Loader::includeModule('main'))
		{
			throw new \RuntimeException('Module main is not available.');
		}

		$this->removeAgentIfExists();
	}

	private function removeAgentIfExists(): void
	{
		while (\CAgent::RemoveAgent(self::AGENT_NAME, self::MODULE_ID))
		{
			// Remove all duplicates deterministically.
		}
	}
}
```

## Notes

- Always remove duplicates before adding (idempotency).
- Keep agent name exact and stable.
- For module uninstall, also remove via `CAgent::RemoveModuleAgents(<module_id>)`.
