I added a `STUDENT` customer type that gets 10% off. A student who is also a loyalty member gets whichever is bigger, the student rate or the loyalty rate, and the two are never combined. All 15 tests pass, including three new ones for the student cases.

- **Rates:** a student with no points gets 10%. With 500–1999 points they still get 10%, since the 5% loyalty rate is smaller. With 2000 or more points they get 15%.
- **Code changes:** the rule is one new line in `DiscountPolicy.java`, which takes the larger of the student and loyalty rates. I also added the enum value and a "student" label on receipts in `ReceiptFormatter.java`.
- **Docs:** the README discount table now lists students and says discounts are never combined.

I didn't commit anything.