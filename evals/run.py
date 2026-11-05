"""Run every eval case under every skill condition and store the raw replies.

Usage: python evals/run.py [--reps 3] [--jobs 6] [--model sonnet] [--case 03-hot-path]
Existing replies are kept, so an interrupted run can simply be restarted; a reply written with a skill that has
changed since is written again.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from harness import RUNS_DIR, SINGLE_TURN_CONDITIONS, Case, Condition, ask_claude, load_cases


@dataclass(frozen=True)
class Job:
    case: Case
    condition: Condition
    rep: int

    @property
    def reply_path(self) -> Path:
        return RUNS_DIR / self.case.case_id / f"{self.condition.name}-r{self.rep}.md"

    def is_current(self) -> bool:
        """The reply exists and was written with the skill as it is now."""
        meta_path = self.reply_path.with_suffix(".json")
        if not (self.reply_path.exists() and meta_path.exists()):
            return False
        skill = self.condition.skill(self.case.language)
        recorded = json.loads(meta_path.read_text(encoding="utf-8")).get("skill_fingerprint")
        return recorded == (skill.fingerprint() if skill else None)


def main() -> None:
    args = _parse_args()
    cases = [case for case in load_cases() if args.case in (None, case.case_id)]
    jobs = [
        Job(case, condition, rep)
        for case in cases
        for condition in SINGLE_TURN_CONDITIONS
        if condition.applies_to(case.language)
        for rep in range(1, args.reps + 1)
    ]
    pending = [job for job in jobs if not job.is_current()]
    print(f"{len(jobs)} runs, {len(pending)} still to do")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_run, job, args.model): job for job in pending}
        for future in as_completed(futures):
            job = futures[future]
            try:
                future.result()
                print(f"done   {job.case.case_id} {job.condition.name} r{job.rep}")
            except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
                print(f"FAILED {job.case.case_id} {job.condition.name} r{job.rep}: {error}")


def _run(job: Job, model: str) -> None:
    skill = job.condition.skill(job.case.language)
    reply = ask_claude(job.case.prompt, job.condition.system_prompt(job.case.language), model)
    meta = {
        "model": model,
        "model_ids": reply.model_ids,
        "duration_ms": reply.duration_ms,
        "cost_usd": reply.cost_usd,
        "output_tokens": reply.output_tokens,
        "skill_fingerprint": skill.fingerprint() if skill else None,
    }
    job.reply_path.parent.mkdir(parents=True, exist_ok=True)
    # The reply file marks a run as done, so it is written last.
    job.reply_path.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    job.reply_path.write_text(reply.text, encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all eval cases under every skill condition.")
    parser.add_argument("--reps", type=int, default=3, help="repetitions per case and condition")
    parser.add_argument("--jobs", type=int, default=6, help="parallel claude processes")
    parser.add_argument("--model", default="sonnet", help="model that does the coding tasks")
    parser.add_argument("--case", help="run only this case id")
    return parser.parse_args()


if __name__ == "__main__":
    main()
