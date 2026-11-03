export interface PricedItem {
  price: number;
  category?: string;
}

const BOOK_CATEGORY = "books";
const MEMBER_BOOK_RATE = 0.9;
const MEMBER_DEFAULT_RATE = 0.95;
const SAVE10_CODE = "SAVE10";
const SAVE10_AMOUNT = 10;

export function getPrice(item: PricedItem, isMember: boolean, coupon?: string): number {
  let price = item.price;
  if (isMember) {
    price *= item.category === BOOK_CATEGORY ? MEMBER_BOOK_RATE : MEMBER_DEFAULT_RATE;
  }
  if (coupon === SAVE10_CODE) {
    price = Math.max(0, price - SAVE10_AMOUNT);
  }
  return roundToCents(price);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
