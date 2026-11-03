# Adding a subscription pause event (TypeScript)

Tests extending a discriminated union that is consumed by three exhaustive switches (state reducer, audit log serializer, notifier), each ending in the codebase's `assertNever`. A careful change adds the event once in `src/events.ts`, handles it in all three places without `default` fallbacks, `any` or non-null assertions, and notices the interactions the prompt spells out (payment events must not move a paused subscription, cancelling clears the resume date). The existing `payment_failed` guard only excludes `canceled`, so adding the new status silently lets a payment failure turn a paused subscription past due unless the reducer is updated. Behavior the prompt does not ask for (extra emails, extra data fields, resuming) must not appear.

## Prompt

We want customers to be able to pause their subscription, so billing needs a new `subscription_paused` event. It carries `resumeOn` (the date billing picks up again, as `YYYY-MM-DD`) and a `reason` (free text, like the cancellation reason). Here is how it should behave:

- State: an active subscription becomes `paused`, and the subscription remembers `resumeOn` (it is `null` whenever the subscription is not paused). Only an active subscription can be paused; in any other status the event changes nothing. While paused, nothing is billed, so payment events leave a paused subscription as it is. Cancelling a paused subscription works as usual and also clears `resumeOn`.
- Audit log: same line format as the other events, with the resume date and then the reason (quoted the way the cancellation reason is), e.g. `2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- Notifications: the customer gets a `subscription-paused` email that carries the resume date as `resumeOn`. Nobody else is notified.

Resuming is a separate piece of work, so leave that out. Please add tests too.
