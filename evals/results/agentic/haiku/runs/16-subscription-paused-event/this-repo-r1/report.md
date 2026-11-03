The `subscription_paused` event is in place across state, audit log and notifications, with tests. All 20 tests pass (13 existing, 7 new) and `npm run typecheck` is clean. I did not commit anything.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the union.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field on the subscription, `null` unless paused.
  - Pausing only works from `active`; from any other status the state is returned unchanged.
  - `payment_failed` is ignored while paused, the same way it already is for canceled. `payment_recovered` already ignores anything that isn't `past_due`, so it needed no change.
  - Cancelling sets `resumeOn` back to `null`.
- **`src/audit.ts`**: `resumeOn=2025-05-01 reason="vacation"`, with the reason quoted like the cancellation reason.
- **`src/notifier.ts`**: one `subscription-paused` email to the customer, carrying only `resumeOn`.
- **Tests**: one per module, plus state tests for the non-active statuses, a repeated pause keeping the original date, payments on a paused subscription, and cancelling while paused.

**Choices I made that you may want to change**

- The `subscription-paused` email carries only `resumeOn`, not the reason. Your spec named only the resume date, so I left the reason out. The cancellation email does include its reason, so say if you want it here too.
- Pausing an already paused subscription is ignored, so the first resume date stays. The spec only covered non-active statuses, so this was my call.
- `plan_changed` still applies while paused. The spec didn't mention it.
- `resumeOn` is typed as a plain `string` with no format check, matching how `occurredAt` is handled. A malformed date will pass through.

Resuming is not included, as you asked.