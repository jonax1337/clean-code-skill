import { assertNever } from "./assert-never.ts";
import type { PaymentFailed, SubscriptionEvent } from "./events.ts";

export interface Notification {
  audience: "customer" | "billing-team";
  template: string;
  data: Record<string, string>;
}

/** After this many failed charges the billing team steps in. */
const ESCALATION_ATTEMPT = 3;

/** The emails an event triggers, in the order they are sent. */
export function notificationsFor(event: SubscriptionEvent): Notification[] {
  switch (event.type) {
    case "subscription_started":
      return [{ audience: "customer", template: "welcome", data: { plan: event.plan } }];
    case "plan_changed":
      return [{ audience: "customer", template: "plan-changed", data: { from: event.from, to: event.to } }];
    case "payment_failed":
      return paymentFailedNotifications(event);
    case "payment_recovered":
      return [];
    case "subscription_canceled":
      return [{ audience: "customer", template: "subscription-canceled", data: { reason: event.reason } }];
    default:
      return assertNever(event);
  }
}

function paymentFailedNotifications(event: PaymentFailed): Notification[] {
  const data = { attempt: String(event.attempt) };
  const notifications: Notification[] = [{ audience: "customer", template: "payment-failed", data }];
  if (event.attempt >= ESCALATION_ATTEMPT) {
    notifications.push({ audience: "billing-team", template: "payment-escalation", data });
  }
  return notifications;
}
