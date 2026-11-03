import { assertNever } from "./assert-never.ts";
import type { SubscriptionEvent } from "./events.ts";

/** One line for the audit log: timestamp, subscription id, event type, then the event's details. */
export function serializeAuditEntry(event: SubscriptionEvent): string {
  const entry = `${event.occurredAt} ${event.subscriptionId} ${event.type}`;
  const details = auditDetails(event);
  return details === "" ? entry : `${entry} ${details}`;
}

function auditDetails(event: SubscriptionEvent): string {
  switch (event.type) {
    case "subscription_started":
      return `plan=${event.plan}`;
    case "plan_changed":
      return `from=${event.from} to=${event.to}`;
    case "payment_failed":
      return `attempt=${event.attempt}`;
    case "payment_recovered":
      return "";
    case "subscription_canceled":
      return `reason=${JSON.stringify(event.reason)}`;
    default:
      return assertNever(event);
  }
}
