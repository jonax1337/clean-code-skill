The `subscription_paused` event is in place across state, audit log, and notifications, with tests. All 20 tests pass and the typecheck is clean. I haven't committed or pushed, since you didn't ask for that.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field, which is `null` unless paused.
  - Pausing only works from `active`; any other status is returned unchanged.
  - Payment failures are ignored while paused, so the subscription stays paused.
  - Payment recovery needed no change, since it already only acts on `past_due`.
  - Cancelling sets `resumeOn` back to `null`.
- **`src/audit.ts`**: `resumeOn=… reason="…"`, with the reason quoted the same way as cancellation.
- **`src/notifier.ts`**: one `subscription-paused` email to the customer, with only `resumeOn` in its data.

**Tests**

- I wrote the tests first and watched them fail for the expected reasons before implementing.
- They cover the pause transition, that pausing from other statuses changes nothing, payment events leaving a paused subscription alone, cancelling a paused subscription, the audit line, and the email.

**Choices I made**

- `resumeOn` is typed as a plain string, documented as `YYYY-MM-DD`, and not checked at runtime. Adding a format check is a small follow-up if you want one.
- The pause email carries only `resumeOn`, not the reason, because the spec named only the date.

**Not done**

- The skill's `crapper`, `dryer`, and `mutator` tools aren't installed in this repo, so I didn't run the complexity, duplication, or mutation checks.
- Nothing is committed or pushed. The changes are in the working tree; say the word and I'll commit them in small steps and push to `main`.
- Resuming is left out, as you asked.