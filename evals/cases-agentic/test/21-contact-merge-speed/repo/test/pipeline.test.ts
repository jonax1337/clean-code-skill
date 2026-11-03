import assert from "node:assert/strict";
import { test } from "node:test";
import { importCsv } from "../src/pipeline.ts";

const HEADER = "id,email,name,phone,tags,updatedAt";

test("importCsv merges the upload into the stored book", () => {
  const stored = `${HEADER}\n1,a@x.io,Ada,,vip,10\n`;
  const uploaded = `${HEADER}\n2,A@x.io,,555,beta,20\n3,b@x.io,Bob,,,5\n`;
  assert.equal(
    importCsv(stored, uploaded),
    `${HEADER}\n1,a@x.io,Ada,555,vip;beta,20\n3,b@x.io,Bob,,,5\n`,
  );
});
