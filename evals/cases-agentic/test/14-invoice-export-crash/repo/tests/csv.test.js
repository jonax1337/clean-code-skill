import assert from "node:assert/strict";
import { test } from "node:test";
import { toCsv } from "../src/csv.js";

test("toCsv ends every row with a newline", () => {
  assert.equal(toCsv([["a", "b"], ["c", "d"]]), "a,b\nc,d\n");
});

test("toCsv quotes cells with commas, quotes and line breaks", () => {
  assert.equal(toCsv([['a,b', 'say "hi"', "x\ny"]]), '"a,b","say ""hi""","x\ny"\n');
});
