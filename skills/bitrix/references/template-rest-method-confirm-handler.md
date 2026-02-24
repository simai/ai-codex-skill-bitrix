# Template: REST Method Confirm Handler

Use this template for methods requiring admin confirmation.

## Trigger Pattern

When calling protected method:

- if response is `METHOD_CONFIRM_WAITING`, store pending operation context and stop immediate retry loop
- if response is `METHOD_CONFIRM_DENIED`, mark operation terminal and notify operator/user

## Data to Persist

- token
- method name
- request payload hash
- created timestamp
- operation id
- retries count

## Event Handling

On `OnAppMethodConfirm`:

1. validate `application_token`
2. read `TOKEN`, `METHOD`, `CONFIRMED`
3. find pending operation by token + method
4. if `CONFIRMED=1`, execute pending operation once
5. if `CONFIRMED=0`, close operation as denied

## Safety Rules

- confirmation is token-bound, not global
- on token rotation, old confirmation state is invalid
- no infinite retries while waiting for confirmation

## Operator Diagnostics

Required log fields:

- portal/member id
- method
- token hash (masked)
- confirmation state
- final outcome (executed/denied/expired)

## Expiry Policy

- pending confirmations must have TTL
- expired pending operations require explicit restart by user/operator
