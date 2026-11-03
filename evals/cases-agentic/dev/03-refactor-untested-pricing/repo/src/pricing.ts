export function getPrice(p: any, isMember: boolean, coupon?: string) {
  let price = p.price;
  if (isMember) {
    if (p.category == "books") {
      price = price * 0.9;
    } else {
      price = price * 0.95;
    }
  }
  if (coupon) {
    if (coupon == "SAVE10") {
      price = price - 10;
      if (price < 0) price = 0;
    }
  }
  return Math.round(price * 100) / 100;
}
