import assert from "node:assert/strict";
import { test } from "node:test";
import { dueJobs, nextRun } from "../src/scheduler.ts";

test("nextRun adds the interval to the last run", () => {
  assert.equal(nextRun({ name: "sync", every: "15m", lastRun: 1_000 }), 1_000 + 900_000);
});

test("dueJobs returns the jobs whose next run has been reached", () => {
  const jobs = [
    { name: "sync", every: "1m", lastRun: 0 },
    { name: "cleanup", every: "1h", lastRun: 0 },
  ];
  assert.deepEqual(
    dueJobs(jobs, 120_000).map((job) => job.name),
    ["sync"],
  );
});
