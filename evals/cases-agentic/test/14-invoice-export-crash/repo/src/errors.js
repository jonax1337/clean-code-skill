/** A record refers to something that does not exist, for example an invoice to an unknown customer. */
export class UnknownReferenceError extends Error {
  constructor(kind, id, referencedBy) {
    const origin = referencedBy ? ` (referenced by ${referencedBy})` : "";
    super(`Unknown ${kind} "${id}"${origin}`);
    this.name = "UnknownReferenceError";
    this.kind = kind;
    this.id = id;
  }
}
