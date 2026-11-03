# Agentic eval results

A coding agent with Read/Grep/Glob/Edit/Write/Bash works on a fresh copy of a fixture repo; deterministic
checks grade the result and a blind judge compares runs pairwise. `dev` cases may have shaped the skill;
`test` cases are held out. Cases are weighted equally. Brackets are 95 % bootstrap intervals that resample
runs within each case, so they describe these cases only.

## Coder: haiku

### test cases (6)

| Condition | Runs | Checks passed | Δ vs no skill | Δ vs v2 | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 18 | 98% [96%–99%] | – | +1 pts [-1 to +3] | 14/18 | $0.006 | 14.3 |
| This repo, v2 | 18 | 97% [96%–98%] | -1 pts [-3 to +2] | – | 13/18 | $0.008 | 15.1 |
| This repo, v3 | 18 | 97% [96%–98%] | -1 pts [-3 to +1] | +0 pts [-2 to +2] | 13/18 | $0.009 | 14.3 |
| v3b: lean | 18 | 97% [96%–99%] | -1 pts [-3 to +2] | +0 pts [-2 to +2] | 13/18 | $0.008 | 15.4 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory |
|---|---|---|---|---|
| This repo, v2 vs This repo, v3 | 18 | 0.38 [0.24–0.51] | 6 / 2 / 10 | 6% |

#### Checks by case (passed / runs)

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| shares_add_up | 3/3 | 3/3 | 3/3 | 3/3 |
| invalid_input_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| equal_split_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| no_float_money | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 2/3 | 3/3 | 3/3 | 3/3 |
| tests_added | 3/3 | 3/3 | 3/3 | 3/3 |
| readme_updated | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 2/3 | 2/3 | 2/3 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| blank_lines_skipped | 3/3 | 3/3 | 3/3 | 3/3 |
| malformed_lines_still_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| no_catch_all_handler | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_test_added | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| flag_is_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| other_behavior_preserved | 3/3 | 3/3 | 3/3 | 3/3 |
| builds_without_warnings | 3/3 | 3/3 | 3/3 | 3/3 |
| no_leftovers | 3/3 | 3/3 | 3/3 | 3/3 |
| other_tests_kept | 3/3 | 3/3 | 3/3 | 3/3 |
| changelog_entry | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| parser_returns_milliseconds | 3/3 | 3/3 | 3/3 | 3/3 |
| timing_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| unit_sensitive_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| doc_comment_states_new_unit | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 2/3 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| same_result_as_before | 3/3 | 3/3 | 3/3 | 3/3 |
| inputs_not_modified | 3/3 | 3/3 | 3/3 | 3/3 |
| work_grows_linearly | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_second_normalization | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 1/3 | 0/3 | 0/3 | 2/3 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| totals_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| failures_and_side_effects_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 2/3 | 3/3 | 2/3 |
| new_tests_pass_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_function_longer_than_thirty_lines | 3/3 | 3/3 | 3/3 | 3/3 |
| public_interface_and_refund_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 2/3 | 3/3 | 2/3 | 2/3 |

## Coder: opus

### test cases (6)

| Condition | Runs | Checks passed | Δ vs no skill | Δ vs v2 | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 18 | 98% [98%–98%] | – | +0 pts [+0 to +0] | 15/18 | $0.194 | 10.9 |
| This repo, v2 | 18 | 98% [98%–98%] | +0 pts [+0 to +0] | – | 15/18 | $0.241 | 10.8 |
| This repo, v3 | 18 | 99% [98%–100%] | +1 pts [+0 to +2] | +1 pts [+0 to +2] | 16/18 | $0.249 | 10.0 |
| v3b: lean | 18 | 99% [98%–100%] | +1 pts [+0 to +2] | +1 pts [+0 to +2] | 16/18 | $0.222 | 10.3 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory |
|---|---|---|---|---|
| This repo, v2 vs This repo, v3 | 18 | 0.32 [0.21–0.42] | 3 / 6 / 9 | 28% |

#### Checks by case (passed / runs)

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| shares_add_up | 3/3 | 3/3 | 3/3 | 3/3 |
| invalid_input_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| equal_split_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| no_float_money | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_added | 3/3 | 3/3 | 3/3 | 3/3 |
| readme_updated | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| blank_lines_skipped | 3/3 | 3/3 | 3/3 | 3/3 |
| malformed_lines_still_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| no_catch_all_handler | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_test_added | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| flag_is_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| other_behavior_preserved | 3/3 | 3/3 | 3/3 | 3/3 |
| builds_without_warnings | 3/3 | 3/3 | 3/3 | 3/3 |
| no_leftovers | 3/3 | 3/3 | 3/3 | 3/3 |
| other_tests_kept | 3/3 | 3/3 | 3/3 | 3/3 |
| changelog_entry | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| parser_returns_milliseconds | 3/3 | 3/3 | 3/3 | 3/3 |
| timing_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| unit_sensitive_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| doc_comment_states_new_unit | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| same_result_as_before | 3/3 | 3/3 | 3/3 | 3/3 |
| inputs_not_modified | 3/3 | 3/3 | 3/3 | 3/3 |
| work_grows_linearly | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_second_normalization | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 0/3 | 0/3 | 1/3 | 1/3 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| totals_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| failures_and_side_effects_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| new_tests_pass_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_function_longer_than_thirty_lines | 3/3 | 3/3 | 3/3 | 3/3 |
| public_interface_and_refund_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 |

## Coder: sonnet

### dev cases (3)

| Condition | Runs | Checks passed | Δ vs no skill | Δ vs v2 | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 9 | 70% [70%–70%] | – | -19 pts [-21 to -16] | 0/9 | $0.041 | 5.8 |
| sickn33/clean-code | 9 | 73% [70%–74%] | +2 pts [+0 to +4] | -16 pts [-20 to -12] | 0/9 | $0.050 | 6.4 |
| This repo, v2 | 9 | 89% [86%–91%] | +19 pts [+16 to +21] | – | 4/9 | $0.063 | 8.2 |
| This repo, v3 | 9 | 100% [100%–100%] | +30 pts [+30 to +30] | +11 pts [+9 to +14] | 9/9 | $0.074 | 10.0 |
| v3b: lean | 9 | 100% [100%–100%] | +30 pts [+30 to +30] | +11 pts [+9 to +14] | 9/9 | $0.069 | 10.4 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory |
|---|---|---|---|---|
| No skill vs sickn33/clean-code | 9 | 0.39 [0.33–0.50] | 1 / 5 / 3 | 22% |
| No skill vs This repo, v2 | 9 | 0.14 [0.00–0.33] | 1 / 0 / 8 | 0% |
| sickn33/clean-code vs This repo, v2 | 9 | 0.14 [0.00–0.33] | 1 / 0 / 8 | 0% |
| This repo, v2 vs This repo, v3 | 9 | 0.14 [0.03–0.25] | 0 / 2 / 7 | 0% |
| This repo, v2 vs v3b: lean | 9 | 0.08 [0.00–0.17] | 0 / 1 / 8 | 11% |
| This repo, v3 vs v3b: lean | 9 | 0.61 [0.36–0.83] | 5 / 1 / 3 | 11% |

### test cases (6)

| Condition | Runs | Checks passed | Δ vs no skill | Δ vs v2 | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 18 | 97% [96%–98%] | – | -3 pts [-4 to -2] | 13/18 | $0.058 | 8.3 |
| This repo, v2 | 18 | 100% [100%–100%] | +3 pts [+2 to +4] | – | 18/18 | $0.089 | 9.1 |
| This repo, v3 | 18 | 100% [100%–100%] | +3 pts [+2 to +4] | +0 pts [+0 to +0] | 18/18 | $0.100 | 8.6 |
| v3b: lean | 18 | 98% [97%–99%] | +1 pts [-1 to +3] | -2 pts [-3 to -1] | 15/18 | $0.099 | 10.1 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory |
|---|---|---|---|---|
| This repo, v2 vs This repo, v3 | 18 | 0.22 [0.11–0.33] | 2 / 4 / 12 | 6% |
| This repo, v2 vs v3b: lean | 18 | 0.29 [0.18–0.39] | 4 / 3 / 11 | 11% |

#### Checks by case (passed / runs)

**dev: Add a feature that needs helpers from other modules (Python)**

| Check | No skill | sickn33/clean-code | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| reuses_helpers | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_reimplemented_money_logic | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| test_added | 0/3 | 0/3 | 1/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 |

**dev: Bugfix in a legacy module with a sibling bug (Python)**

| Check | No skill | sickn33/clean-code | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_test | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 |
| sibling_bug | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 |

**dev: Refactor untested code with many callers (TypeScript)**

| Check | No skill | sickn33/clean-code | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| callers_compatible | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| any_replaced | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| magic_numbers_named | 0/3 | 2/3 | 2/3 | 3/3 | 3/3 |
| characterization_tests | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 |
| no_over_engineering | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 | 3/3 | 3/3 |

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| shares_add_up | 3/3 | 3/3 | 3/3 | 3/3 |
| invalid_input_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| equal_split_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| no_float_money | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_added | 3/3 | 3/3 | 3/3 | 3/3 |
| readme_updated | 2/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| blank_lines_skipped | 3/3 | 3/3 | 3/3 | 3/3 |
| malformed_lines_still_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| no_catch_all_handler | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_test_added | 2/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| flag_is_rejected | 3/3 | 3/3 | 3/3 | 3/3 |
| other_behavior_preserved | 3/3 | 3/3 | 3/3 | 3/3 |
| builds_without_warnings | 3/3 | 3/3 | 3/3 | 3/3 |
| no_leftovers | 3/3 | 3/3 | 3/3 | 3/3 |
| other_tests_kept | 3/3 | 3/3 | 3/3 | 3/3 |
| changelog_entry | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| parser_returns_milliseconds | 3/3 | 3/3 | 3/3 | 3/3 |
| timing_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| unit_sensitive_callers_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| doc_comment_states_new_unit | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| same_result_as_before | 3/3 | 3/3 | 3/3 | 3/3 |
| inputs_not_modified | 3/3 | 3/3 | 3/3 | 3/3 |
| work_grows_linearly | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_second_normalization | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 0/3 | 3/3 | 3/3 | 1/3 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo, v2 | This repo, v3 | v3b: lean |
|---|---|---|---|---|
| totals_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| failures_and_side_effects_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| new_tests_pass_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_function_longer_than_thirty_lines | 3/3 | 3/3 | 3/3 | 2/3 |
| public_interface_and_refund_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 |
