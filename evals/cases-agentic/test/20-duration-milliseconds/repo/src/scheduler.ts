import { parseDuration } from "./duration.ts";

export interface Job {
  name: string;
  every: string;
  lastRun: number;
}

/** Timestamp (ms since epoch) at which the job is due again. */
export function nextRun(job: Job): number {
  return job.lastRun + parseDuration(job.every) * 1000;
}

export function dueJobs(jobs: Job[], now: number): Job[] {
  return jobs.filter((job) => nextRun(job) <= now);
}
