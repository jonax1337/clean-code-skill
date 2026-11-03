import assert from "node:assert/strict";
import { test } from "node:test";
import { InvalidAmountError, UnknownCurrencyError } from "../src/errors.ts";
import { convert, feeFor, minorUnitsOf, quote } from "../src/rates.ts";

test("minorUnitsOf knows how many decimals each currency has", () => {
  assert.equal(minorUnitsOf("EUR"), 2);
  assert.equal(minorUnitsOf("USD"), 2);
  assert.equal(minorUnitsOf("CHF"), 2);
  assert.equal(minorUnitsOf("JPY"), 0);
  assert.equal(minorUnitsOf("KWD"), 3);
});

test("minorUnitsOf rejects unknown currencies", () => {
  assert.throws(() => minorUnitsOf("XXX"), UnknownCurrencyError);
});

test("convert applies the rate between two currencies", () => {
  assert.equal(convert(1000, "EUR", "USD"), 1100);
  assert.equal(convert(1100, "USD", "EUR"), 1000);
  assert.equal(convert(1000, "EUR", "CHF"), 950);
  assert.equal(convert(950, "CHF", "USD"), 1100);
});

test("convert leaves an amount unchanged within the same currency", () => {
  assert.equal(convert(12345, "EUR", "EUR"), 12345);
  assert.equal(convert(777, "JPY", "JPY"), 777);
});

test("convert shifts the decimal point between currencies with different minor units", () => {
  assert.equal(convert(100, "EUR", "KWD"), 325);
  assert.equal(convert(325, "KWD", "EUR"), 100);
  assert.equal(convert(1100, "USD", "KWD"), 3250);
  assert.equal(convert(163, "JPY", "EUR"), 100);
});

test("convert rounds amounts that do not divide evenly to the nearest minor unit", () => {
  assert.equal(convert(1, "EUR", "JPY"), 2);
  assert.equal(convert(100000, "USD", "EUR"), 90909);
});

test("convert breaks ties by the rounding mode of the target currency", () => {
  // JPY rounds half up, KWD rounds half to even: 4 EUR cents are 6.5 yen, 2 EUR cents are 6.5 fils.
  assert.equal(convert(4, "EUR", "JPY"), 7);
  assert.equal(convert(100, "EUR", "JPY"), 163);
  assert.equal(convert(2, "EUR", "KWD"), 6);
  assert.equal(convert(10, "EUR", "KWD"), 32);
  assert.equal(convert(6, "EUR", "KWD"), 20);
});

test("convert returns zero for a zero amount", () => {
  assert.equal(convert(0, "EUR", "JPY"), 0);
});

test("convert treats negative amounts like positive ones with the sign kept", () => {
  assert.equal(convert(-1000, "EUR", "USD"), -1100);
  assert.equal(convert(-1, "EUR", "JPY"), -2);
  assert.equal(convert(-4, "EUR", "JPY"), -7);
  assert.equal(convert(-2, "EUR", "KWD"), -6);
});

test("convert rejects amounts that are not whole numbers of minor units", () => {
  assert.throws(() => convert(1.5, "EUR", "USD"), InvalidAmountError);
  assert.throws(() => convert(Number.NaN, "EUR", "USD"), InvalidAmountError);
  assert.throws(() => convert(Number.POSITIVE_INFINITY, "EUR", "USD"), InvalidAmountError);
  assert.throws(() => convert(2 ** 53, "EUR", "USD"), InvalidAmountError);
});

test("convert names the currency it does not know, whether source or target", () => {
  assert.throws(() => convert(100, "XXX", "EUR"), { name: "UnknownCurrencyError", currency: "XXX" });
  assert.throws(() => convert(100, "EUR", "XXX"), { name: "UnknownCurrencyError", currency: "XXX" });
  assert.throws(() => convert(100, "eur", "USD"), UnknownCurrencyError);
});

test("feeFor charges 2.5 percent between the minimum and the maximum", () => {
  assert.equal(feeFor(100000, "EUR"), 2500);
  assert.equal(feeFor(100000, "USD"), 2500);
  assert.equal(feeFor(100000, "JPY"), 2500);
  assert.equal(feeFor(100000, "KWD"), 1500);
});

test("feeFor charges nothing on a zero amount", () => {
  assert.equal(feeFor(0, "EUR"), 0);
  assert.equal(feeFor(0, "JPY"), 0);
});

test("feeFor raises small amounts to the minimum fee", () => {
  assert.equal(feeFor(1, "EUR"), 30);
  assert.equal(feeFor(1160, "EUR"), 30);
  assert.equal(feeFor(1199, "EUR"), 30);
  assert.equal(feeFor(1960, "JPY"), 50);
  assert.equal(feeFor(11960, "KWD"), 300);
});

test("feeFor charges the plain percentage from the minimum fee upwards", () => {
  assert.equal(feeFor(1200, "EUR"), 30);
  assert.equal(feeFor(1240, "EUR"), 31);
  assert.equal(feeFor(2040, "JPY"), 51);
  assert.equal(feeFor(12000, "KWD"), 300);
  assert.equal(feeFor(12040, "KWD"), 301);
});

test("feeFor caps large amounts at the maximum fee", () => {
  assert.equal(feeFor(199960, "EUR"), 4999);
  assert.equal(feeFor(200000, "EUR"), 5000);
  assert.equal(feeFor(200040, "EUR"), 5000);
  assert.equal(feeFor(10000000, "USD"), 5000);
  assert.equal(feeFor(319960, "JPY"), 7999);
  assert.equal(feeFor(320000, "JPY"), 8000);
  assert.equal(feeFor(320040, "JPY"), 8000);
  assert.equal(feeFor(59960, "KWD"), 1499);
  assert.equal(feeFor(60000, "KWD"), 1500);
  assert.equal(feeFor(60040, "KWD"), 1500);
});

test("feeFor breaks ties by the rounding mode of the currency", () => {
  // 1300 minor units are 32.5 in fees; 1380 are 34.5; 1260 are 31.5.
  assert.equal(feeFor(1300, "EUR"), 32);
  assert.equal(feeFor(1300, "CHF"), 32);
  assert.equal(feeFor(1300, "USD"), 33);
  assert.equal(feeFor(1380, "EUR"), 34);
  assert.equal(feeFor(1380, "USD"), 35);
  assert.equal(feeFor(1260, "EUR"), 32);
  assert.equal(feeFor(2020, "JPY"), 51);
  assert.equal(feeFor(12020, "KWD"), 300);
  assert.equal(feeFor(12060, "KWD"), 302);
});

test("feeFor rejects negative amounts", () => {
  assert.throws(() => feeFor(-1, "EUR"), InvalidAmountError);
  assert.throws(() => feeFor(-100000, "USD"), InvalidAmountError);
});

test("feeFor rejects amounts that are not whole numbers of minor units", () => {
  assert.throws(() => feeFor(10.5, "EUR"), InvalidAmountError);
  assert.throws(() => feeFor(Number.NaN, "EUR"), InvalidAmountError);
});

test("feeFor rejects unknown currencies", () => {
  assert.throws(() => feeFor(1000, "XXX"), { name: "UnknownCurrencyError", currency: "XXX" });
});

test("quote converts, charges the fee and returns what is left", () => {
  assert.deepEqual(quote(100000, "USD", "EUR"), { converted: 90909, fee: 2273, net: 88636 });
  assert.deepEqual(quote(10000, "EUR", "JPY"), { converted: 16250, fee: 406, net: 15844 });
  assert.deepEqual(quote(1000000, "EUR", "EUR"), { converted: 1000000, fee: 5000, net: 995000 });
});

test("quote charges the fee under the rules of the target currency", () => {
  // 1 EUR is 163 yen; the 4 yen percentage is raised to the yen minimum of 50, not the euro minimum of 30.
  assert.deepEqual(quote(100, "EUR", "JPY"), { converted: 163, fee: 50, net: 113 });
});

test("quote accepts an amount that exactly covers the fee", () => {
  assert.deepEqual(quote(30, "EUR", "EUR"), { converted: 30, fee: 30, net: 0 });
});

test("quote rejects an amount that does not cover the fee", () => {
  assert.throws(() => quote(29, "EUR", "EUR"), InvalidAmountError);
  assert.throws(() => quote(25, "EUR", "EUR"), InvalidAmountError);
});

test("quote of nothing is nothing", () => {
  assert.deepEqual(quote(0, "EUR", "USD"), { converted: 0, fee: 0, net: 0 });
});

test("quote rejects negative amounts and unknown currencies", () => {
  assert.throws(() => quote(-1000, "EUR", "USD"), InvalidAmountError);
  assert.throws(() => quote(1000, "EUR", "XXX"), UnknownCurrencyError);
  assert.throws(() => quote(1000, "XXX", "EUR"), UnknownCurrencyError);
});
