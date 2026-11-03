export class UnknownCurrencyError extends Error {
  readonly currency: string;

  constructor(currency: string) {
    super(`Unknown currency: ${currency}`);
    this.name = "UnknownCurrencyError";
    this.currency = currency;
  }
}

export class InvalidAmountError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InvalidAmountError";
  }
}
