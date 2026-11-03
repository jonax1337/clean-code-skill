# billing-events

Subscription lifecycle for the billing service. Everything that happens to a subscription is a
`SubscriptionEvent` (`src/events.ts`), and three places consume those events:

- `src/subscription.ts` rebuilds a subscription's current state from its events.
- `src/audit.ts` turns an event into one line for the audit log.
- `src/notifier.ts` decides which emails an event triggers.

Each of them ends its `switch` with `assertNever`, so the compiler tells you where a new event type still
needs handling.

## Setup and tests

```
npm install
npm test            # node --test
npm run typecheck   # tsc --noEmit
```
