import { assertNever } from "./assert-never.ts";
import type { Plan, SubscriptionEvent, SubscriptionStarted } from "./events.ts";

export type SubscriptionStatus = "active" | "past_due" | "canceled";

export interface Subscription {
  id: string;
  plan: Plan;
  status: SubscriptionStatus;
  /** The attempt number of the latest failed charge; 0 while payments are fine. */
  failedAttempts: number;
  startedAt: string;
  canceledAt: string | null;
}

/** The state of a subscription after all of its events, oldest first. The first event must be the start. */
export function replay(events: readonly SubscriptionEvent[]): Subscription {
  const [first, ...rest] = events;
  if (first?.type !== "subscription_started") {
    throw new Error("A subscription history starts with subscription_started");
  }
  return rest.reduce(reduceSubscription, startedSubscription(first));
}

export function reduceSubscription(state: Subscription, event: SubscriptionEvent): Subscription {
  switch (event.type) {
    case "subscription_started":
      // A repeated start event changes nothing.
      return state;
    case "plan_changed":
      return { ...state, plan: event.to };
    case "payment_failed":
      if (state.status === "canceled") {
        return state;
      }
      return { ...state, status: "past_due", failedAttempts: event.attempt };
    case "payment_recovered":
      if (state.status !== "past_due") {
        return state;
      }
      return { ...state, status: "active", failedAttempts: 0 };
    case "subscription_canceled":
      if (state.status === "canceled") {
        return state;
      }
      return { ...state, status: "canceled", canceledAt: event.occurredAt };
    default:
      return assertNever(event);
  }
}

function startedSubscription(event: SubscriptionStarted): Subscription {
  return {
    id: event.subscriptionId,
    plan: event.plan,
    status: "active",
    failedAttempts: 0,
    startedAt: event.occurredAt,
    canceledAt: null,
  };
}
