"""Run the agentic cases: a coding agent with real tools works on a fresh copy of each fixture repo.

Usage: python evals/run_agentic.py [--split dev|test] [--model sonnet] [--conditions baseline,v2] [--reps 3]
                                   [--jobs 3] [--case ID]
Each run stores transcript.jsonl, diff.patch, review.diff, report.md and meta.json in
results/agentic/<model>/runs/<case>/<condition>-r<n>/. Existing runs are kept, so an interrupted run can be restarted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from agentic import AgenticCase, AgentRun, Transcript, load_agentic_cases, results_dir, run_agent
from harness import ALL_CONDITIONS, Condition, write_text_atomic

DEFAULT_CONDITIONS = "baseline,sickn33,v2"
SKILL_DIR_MARKER = "cc-skill-"
# Result subtypes that are the agent's own outcome. Anything else is an infrastructure failure and is retried.
AGENT_OUTCOMES = {"success", "error_max_turns", "error_max_budget_usd"}
# Stream events about the account that ran the eval (quota use), not about the agent's work. Transcripts are
# published, so these are not stored.
ACCOUNT_EVENTS = {"rate_limit_event"}


@dataclass(frozen=True)
class Job:
    case: AgenticCase
    condition: Condition
    rep: int
    model: str

    @property
    def run_dir(self) -> Path:
        return results_dir(self.model, "runs") / self.case.case_id / f"{self.condition.name}-r{self.rep}"


def main() -> None:
    args = _parse_args()
    names = args.conditions.split(",")
    unknown = set(names) - {condition.name for condition in ALL_CONDITIONS}
    if unknown:
        raise SystemExit(f"Unknown conditions: {sorted(unknown)}")
    conditions = [condition for condition in ALL_CONDITIONS if condition.name in names]
    cases = [case for case in load_agentic_cases(args.split) if args.case in (None, case.case_id)]
    jobs = [
        Job(case, condition, rep, args.model)
        for case in cases
        for condition in conditions
        for rep in range(1, args.reps + 1)
    ]
    pending = [job for job in jobs if not (job.run_dir / "meta.json").exists()]
    print(f"{len(jobs)} agent runs with {args.model}, {len(pending)} still to do")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_run, job, args.budget): job for job in pending}
        for future in as_completed(futures):
            job = futures[future]
            label = f"{job.case.case_id} {job.condition.name} r{job.rep}"
            try:
                print(f"done   {label}: {future.result()}")
            except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
                print(f"FAILED {label}: {error}")


def _run(job: Job, budget_usd: float) -> str:
    run = run_agent(job.case, job.condition, job.model, budget_usd)
    transcript = Transcript.from_jsonl(run.transcript_jsonl)
    outcome = transcript.result.get("subtype")
    if outcome not in AGENT_OUTCOMES:
        raise RuntimeError(f"outcome {outcome!r} (exit {run.returncode}): {run.stderr.strip()[-500:]}")
    meta = _meta(job.model, run, transcript)
    job.run_dir.mkdir(parents=True, exist_ok=True)
    (job.run_dir / "transcript.jsonl").write_text(
        _without_account_events(run.transcript_jsonl), encoding="utf-8", newline="\n"
    )
    (job.run_dir / "diff.patch").write_bytes(run.patch.encode("utf-8"))  # exact bytes, CRs included
    (job.run_dir / "review.diff").write_text(run.review_diff, encoding="utf-8", newline="\n")
    (job.run_dir / "report.md").write_text(transcript.final_message, encoding="utf-8", newline="\n")
    # meta.json marks a run as done, so it is written last.
    write_text_atomic(job.run_dir / "meta.json", json.dumps(meta, indent=2))
    return f"{meta['outcome']}, {meta['num_turns']} turns, ${meta['cost_usd']:.3f}"


def _without_account_events(transcript_jsonl: str) -> str:
    return "".join(
        line
        for line in transcript_jsonl.splitlines(keepends=True)
        if not (line.lstrip().startswith("{") and json.loads(line).get("type") in ACCOUNT_EVENTS)
    )


def _meta(model: str, run: AgentRun, transcript: Transcript) -> dict:
    result = transcript.result
    return {
        "model": model,
        "model_ids": sorted(result.get("modelUsage", {})),
        "outcome": result.get("subtype", "unknown"),
        "is_error": result.get("is_error", False),
        "cost_usd": result.get("total_cost_usd", 0.0),
        "duration_ms": result.get("duration_ms", 0),
        "num_turns": result.get("num_turns", 0),
        "output_tokens": result.get("usage", {}).get("output_tokens", 0),
        "permission_denials": len(result.get("permission_denials", [])),
        "tools": transcript.init.get("tools", []),
        "skill_files_read": [
            path.replace("\\", "/").split("/skill/", 1)[-1]
            for path in transcript.files_read()
            if SKILL_DIR_MARKER in path
        ],
        "returncode": run.returncode,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the agentic cases under the chosen skill conditions.")
    parser.add_argument("--split", choices=["dev", "test"], help="run only this split (default: all cases)")
    parser.add_argument("--model", default="sonnet", help="model that does the coding tasks")
    parser.add_argument("--conditions", default=DEFAULT_CONDITIONS, help="comma-separated condition names")
    parser.add_argument("--reps", type=int, default=3, help="repetitions per case and condition")
    parser.add_argument("--jobs", type=int, default=3, help="parallel agent processes")
    parser.add_argument("--budget", type=float, default=2.0, help="spending cap per agent run in USD")
    parser.add_argument("--case", help="run only this case id")
    return parser.parse_args()


if __name__ == "__main__":
    main()
