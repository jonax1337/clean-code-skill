import { parseDuration } from "./duration.ts";

interface Entry<V> {
  value: V;
  expiresAt: number;
}

export class TtlCache<V> {
  private readonly entries = new Map<string, Entry<V>>();
  private readonly defaultTtl: string;

  constructor(defaultTtl: string) {
    this.defaultTtl = defaultTtl;
  }

  set(key: string, value: V, ttl: string = this.defaultTtl, now: number = Date.now()): void {
    this.entries.set(key, { value, expiresAt: now + parseDuration(ttl) });
  }

  get(key: string, now: number = Date.now()): V | undefined {
    const entry = this.entries.get(key);
    if (entry === undefined) {
      return undefined;
    }
    if (entry.expiresAt <= now) {
      this.entries.delete(key);
      return undefined;
    }
    return entry.value;
  }
}
