"""Grade the stored replies blind: one judge call per case and repetition sees all conditions at once.

Usage: python evals/judge.py [--jobs 4] [--model opus]
The judge sees the replies under shuffled letters, never the condition names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import string
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from harness import CONDITIONS, GRADES_DIR, RUNS_DIR, Case, ask_claude, load_cases

JUDGE_SYSTEM_PROMPT = (
    "You are a strict senior code reviewer grading answers from coding assistants. You only output JSON."
)


def main() -> None:
    args = _parse_args()
    tasks = [(case, rep) for case in load_cases() for rep in _reps_with_all_replies(case)]
    pending = [(case, rep) for case, rep in tasks if not _grade_path(case, rep).exists()]
    print(f"{len(tasks)} judge calls, {len(pending)} still to do")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_grade, case, rep, args.model): (case, rep) for case, rep in pending}
        for future in as_completed(futures):
            case, rep = futures[future]
            try:
                future.result()
                print(f"graded {case.case_id} r{rep}")
            except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
                print(f"FAILED {case.case_id} r{rep}: {error}")


def _reps_with_all_replies(case: Case) -> list[int]:
    case_dir = RUNS_DIR / case.case_id
    reps = sorted({int(path.stem.rsplit("-r", 1)[1]) for path in case_dir.glob("*-r*.md")})
    return [
        rep
        for rep in reps
        if all((case_dir / f"{condition.name}-r{rep}.md").exists() for condition in CONDITIONS)
    ]


def _grade_path(case: Case, rep: int):
    return GRADES_DIR / f"{case.case_id}-r{rep}.json"


def _grade(case: Case, rep: int, model: str) -> None:
    blind_map = _blind_map(case, rep)
    replies = {
        letter: (RUNS_DIR / case.case_id / f"{condition}-r{rep}.md").read_text(encoding="utf-8")
        for letter, condition in blind_map.items()
    }
    reply = ask_claude(_judge_prompt(case, replies), JUDGE_SYSTEM_PROMPT, model, effort="high")
    verdicts = _parse_json(reply.text)
    results = {blind_map[letter]: _with_assertion_texts(case, verdicts[letter]) for letter in blind_map}
    GRADES_DIR.mkdir(parents=True, exist_ok=True)
    grade = {
        "case": case.case_id,
        "rep": rep,
        "judge_model": model,
        "blind_map": blind_map,
        "results": results,
    }
    _grade_path(case, rep).write_text(json.dumps(grade, indent=2), encoding="utf-8")


def _blind_map(case: Case, rep: int) -> dict[str, str]:
    """Deterministic shuffle per case and repetition, so reruns produce the same lettering."""
    seed = int(hashlib.sha256(f"{case.case_id}:{rep}".encode()).hexdigest(), 16)
    names = [condition.name for condition in CONDITIONS]
    random.Random(seed).shuffle(names)
    return dict(zip(string.ascii_uppercase, names))


def _judge_prompt(case: Case, replies: dict[str, str]) -> str:
    assertions = "\n".join(f"{number}. {text}" for number, text in enumerate(case.assertions, 1))
    answers = "\n\n".join(f'<answer id="{letter}">\n{text}\n</answer>' for letter, text in replies.items())
    letters = ", ".join(replies)
    return f"""Several coding assistants answered the same task. Grade every answer on its own.

<task>
{case.prompt}
</task>

<assertions>
{assertions}
</assertions>

{answers}

For each answer ({letters}) decide for every assertion whether it is clearly satisfied. Pass only
when the answer itself shows it; do not give credit for intentions. Then give an overall quality
score from 1 to 10 for how much you would want this answer in your codebase.

Return only this JSON, with one entry per answer id:
{{"A": {{"assertions": [{{"n": 1, "passed": true, "evidence": "short quote or reason"}}], "quality": 7}}}}"""


def _parse_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Judge reply contains no JSON: {text[:200]}")
    return json.loads(text[start : end + 1])


def _with_assertion_texts(case: Case, verdict: dict) -> dict:
    by_number = {item["n"]: item for item in verdict["assertions"]}
    assertions = [
        {
            "text": text,
            "passed": bool(by_number[number]["passed"]),
            "evidence": by_number[number].get("evidence", ""),
        }
        for number, text in enumerate(case.assertions, 1)
    ]
    return {"assertions": assertions, "quality": verdict["quality"]}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade stored replies blind with a judge model.")
    parser.add_argument("--jobs", type=int, default=4, help="parallel judge processes")
    parser.add_argument("--model", default="opus", help="judge model")
    return parser.parse_args()


if __name__ == "__main__":
    main()
