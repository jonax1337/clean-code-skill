export type Plan = "basic" | "pro" | "enterprise";

interface EventBase {
  subscriptionId: string;
  /** When it happened, as an ISO 8601 timestamp in UTC. */
  occurredAt: string;
}

export interface SubscriptionStarted extends EventBase {
  type: "subscription_started";
  plan: Plan;
}

export interface PlanChanged extends EventBase {
  type: "plan_changed";
  from: Plan;
  to: Plan;
}

export interface PaymentFailed extends EventBase {
  type: "payment_failed";
  /** 1 for the first failed charge, 2 for the retry after it, and so on. */
  attempt: number;
}

export interface PaymentRecovered extends EventBase {
  type: "payment_recovered";
}

export interface SubscriptionCanceled extends EventBase {
  type: "subscription_canceled";
  reason: string;
}

export type SubscriptionEvent =
  | SubscriptionStarted
  | PlanChanged
  | PaymentFailed
  | PaymentRecovered
  | SubscriptionCanceled;
