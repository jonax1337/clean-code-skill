# Agentic eval results

A coding agent with Read/Grep/Glob/Edit/Write/Bash works on a fresh copy of a fixture repo; deterministic
checks grade the result and a blind judge compares runs pairwise. `dev` cases may have shaped the skill;
`test` cases are held out. Cases are weighted equally. Brackets are 95 % bootstrap intervals that resample
runs within each case, so they describe these cases only; where a condition has one run per case, they
resample the cases instead.

## Coder: opus

### test cases (13)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 26 | 97% [96%–98%] | – | -1 pts [-2 to +1] | 19/26 | $0.244 | 10.3 |
| This repo | 26 | 98% [97%–99%] | +1 pts [-1 to +2] | – | 21/26 | $0.329 | 10.5 |
| unclebob/ub-mode | 26 | 94% [93%–95%] | -3 pts [-5 to -1] | -3 pts [-5 to -2] | 15/26 | $0.358 | 12.1 |
| sickn33/clean-code | 26 | 99% [98%–99%] | +2 pts [+1 to +3] | +1 pts [+0 to +2] | 23/26 | $0.264 | 11.1 |
| ertugrul-dmr/clean-code | 14 | 99% [99%–100%] | – | – | 13/14 | $0.229 | 8.1 |
| btseee/clean-code | 13 | 97% [94%–100%] | +0 pts [-1 to +1] | -0 pts [-3 to +2] | 10/13 | $0.283 | 9.2 |
| CLAUDE.md baseline | 13 | 99% [96%–100%] | +2 pts [-2 to +6] | +1 pts [-2 to +5] | 12/13 | $0.257 | 9.2 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 24 | 0% | 8% | 19.7 | 6.1 |
| This repo | 24 | 0% | 8% | 19.0 | 5.8 |
| unclebob/ub-mode | 24 | 0% | 8% | 18.6 | 5.6 |
| sickn33/clean-code | 24 | 0% | 8% | 17.2 | 5.4 |
| ertugrul-dmr/clean-code | 12 | 0% | 17% | 18.9 | 5.6 |
| btseee/clean-code | 12 | 0% | 8% | 20.0 | 6.2 |
| CLAUDE.md baseline | 12 | 0% | 8% | 20.7 | 6.3 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 26 | 0.29 [0.23–0.35] | 7 / 1 / 18 | 0% | 0.47 | 0.48 | 0.58 | 0.24 | 0.46 | 0.30 |
| This repo vs unclebob/ub-mode | 26 | 0.81 [0.75–0.87] | 19 / 4 / 3 | 15% | 0.49 | 0.50 | 0.54 | 0.89 | 0.78 | 0.46 |
| This repo vs sickn33/clean-code | 26 | 0.74 [0.64–0.84] | 18 / 3 / 5 | 12% | 0.55 | 0.50 | 0.47 | 0.69 | 0.55 | 0.72 |
| This repo vs ertugrul-dmr/clean-code | 14 | 0.59 [0.46–0.71] | 7 / 3 / 4 | 14% | 0.43 | 0.41 | 0.48 | 0.68 | 0.59 | 0.50 |
| This repo vs btseee/clean-code | 13 | 0.60 [0.37–0.81] | 6 / 3 / 4 | 23% | 0.54 | 0.38 | 0.38 | 0.54 | 0.50 | 0.71 |
| This repo vs CLAUDE.md baseline | 13 | 0.54 [0.31–0.77] | 6 / 2 / 5 | 15% | 0.44 | 0.44 | 0.48 | 0.71 | 0.52 | 0.48 |

#### Checks by case (passed / runs)

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| shares_add_up | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| invalid_input_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| equal_split_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_float_money | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| readme_updated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 1/2 | 2/2 | 0/2 | 2/2 | 2/2 | 0/1 | 1/1 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| blank_lines_skipped | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| malformed_lines_still_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_catch_all_handler | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 0/2 | 0/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| regression_test_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 2/2 | 2/2 | 1/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| flag_is_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| other_behavior_preserved | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| builds_without_warnings | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_leftovers | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| other_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| changelog_entry | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Refund command for the order service (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| refund_follows_business_rules | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| refund_rejects_bad_input | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| refund_money_is_exact | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| new_tests_cover_refund | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| handler_follows_the_pattern | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| money_stays_decimal | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_console_output | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Invoice export crashes for some customers (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| customers_of_both_systems_get_their_own_name | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unknown_customer_still_fails_loudly | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unknown_customer_error_names_the_customer | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| export_format_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_guard_at_the_crash_site | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| regression_test_fails_on_original_code | 1/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Reviewing a pull request (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| finds_the_sql_injection | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| finds_the_wrong_page_count | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| finds_the_swallowed_audit_error | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| findings_cite_file_and_line | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| decoy_not_reported_as_bug | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| injection_before_style_remarks | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| does_not_approve | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_review_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| pr_not_left_applied | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| looked_at_the_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Adding a subscription pause event (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| reducer_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| audit_log_records_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| notifier_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| exhaustiveness_guard_kept | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_type_escape_hatches | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| event_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_the_requested_event_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_cover_all_three_sites | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Cleaning up a hot-path tokenizer (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| token_stream_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| public_api_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tokenizing_does_not_allocate | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_allocating_code_in_tokenizer | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| functions_are_short | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| blank_test_not_repeated | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 1/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clippy_clean | 2/2 | 2/2 | 1/2 | 2/2 | 1/1 | 0/1 |
| clean_diff | 2/2 | 2/2 | 1/2 | 2/2 | 1/1 | 0/1 |
| tests_run_after_edit | 2/2 | 1/2 | 0/2 | 2/2 | 1/1 | 1/1 |

**test: Making configuration errors visible (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| malformed_values_fail_naming_key_and_value | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| missing_required_keys_and_unreadable_file_fail | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| optional_keys_and_valid_files_unchanged | 2/2 | 1/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| entry_point_refuses_to_start_cleanly | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_swallowing_catch_in_config_package | 2/2 | 1/2 | 0/2 | 0/2 | 0/1 | 1/1 |
| caught_exceptions_keep_their_cause | 0/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_exit_outside_the_entry_point | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_assert_the_new_failures | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 0/2 | 0/2 | 0/2 | 1/2 | 0/1 | 1/1 |

**test: Pulling the user validation into one place (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| create_behavior_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| update_stays_partial | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| invite_keeps_its_differences | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unrelated_handlers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| email_drift_handled | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| validation_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_new_dependency | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_added_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 1/2 | 2/2 | 0/2 | 2/2 | 1/1 | 1/1 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| parser_returns_milliseconds | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| timing_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unit_sensitive_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| doc_comment_states_new_unit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| same_result_as_before | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| inputs_not_modified | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| work_grows_linearly | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_second_normalization | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 0/2 | 2/2 | 2/2 | 1/2 | 1/2 | 0/1 | 1/1 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| totals_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| failures_and_side_effects_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| new_tests_pass_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_function_longer_than_thirty_lines | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| public_interface_and_refund_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 1/2 | 2/2 | 2/2 | 1/1 | 1/1 |

## Coder: sonnet

### dev cases (7)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 21 | 82% [78%–85%] | – | -17 pts [-21 to -15] | 8/21 | $0.079 | 8.9 |
| This repo | 21 | 100% [99%–100%] | +17 pts [+15 to +21] | – | 20/21 | $0.148 | 12.2 |
| unclebob/ub-mode | 21 | 95% [92%–98%] | +13 pts [+8 to +18] | -4 pts [-8 to -2] | 15/21 | $0.097 | 8.6 |
| sickn33/clean-code | 21 | 88% [88%–89%] | +6 pts [+3 to +10] | -11 pts [-12 to -10] | 9/21 | $0.092 | 8.8 |
| ertugrul-dmr/clean-code | 15 | 89% [87%–90%] | – | – | 6/15 | $0.079 | 8.0 |
| btseee/clean-code | 7 | 96% [89%–100%] | +13 pts [+6 to +20] | -4 pts [-11 to +1] | 5/7 | $0.096 | 7.1 |
| CLAUDE.md baseline | 7 | 93% [86%–100%] | +11 pts [+3 to +19] | -6 pts [-14 to +1] | 5/7 | $0.086 | 10.3 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 18 | 0% | 11% | 18.1 | 6.0 |
| This repo | 18 | 0% | 0% | 12.9 | 4.5 |
| unclebob/ub-mode | 18 | 0% | 6% | 15.7 | 5.2 |
| sickn33/clean-code | 18 | 0% | 0% | 16.3 | 5.5 |
| ertugrul-dmr/clean-code | 12 | 0% | 0% | 10.8 | 3.8 |
| btseee/clean-code | 6 | 0% | 0% | 15.0 | 5.2 |
| CLAUDE.md baseline | 6 | 17% | 17% | 18.8 | 6.3 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 21 | 0.02 [0.00–0.07] | 0 / 1 / 20 | 5% | 0.39 | 0.32 | 0.37 | 0.24 | 0.51 | 0.02 |
| This repo vs unclebob/ub-mode | 21 | 0.95 [0.90–1.00] | 19 / 2 / 0 | 10% | 0.61 | 0.64 | 0.67 | 0.87 | 0.69 | 0.90 |

### test cases (13)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 26 | 96% [95%–98%] | – | -2 pts [-4 to -1] | 16/26 | $0.092 | 9.3 |
| This repo | 26 | 98% [98%–99%] | +2 pts [+1 to +4] | – | 23/26 | $0.167 | 12.8 |
| unclebob/ub-mode | 26 | 97% [96%–97%] | +0 pts [-1 to +2] | -2 pts [-3 to -1] | 19/26 | $0.113 | 10.0 |
| sickn33/clean-code | 26 | 99% [99%–99%] | +2 pts [+1 to +4] | +0 pts [+0 to +1] | 22/26 | $0.126 | 12.6 |
| ertugrul-dmr/clean-code | 14 | 98% [97%–99%] | – | – | 11/14 | $0.093 | 8.9 |
| btseee/clean-code | 13 | 96% [92%–99%] | -0 pts [-3 to +3] | -2 pts [-5 to +0] | 9/13 | $0.115 | 9.5 |
| CLAUDE.md baseline | 13 | 99% [97%–100%] | +3 pts [+1 to +5] | +0 pts [-1 to +2] | 11/13 | $0.110 | 10.5 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 24 | 0% | 8% | 20.3 | 6.5 |
| This repo | 24 | 0% | 8% | 19.3 | 6.0 |
| unclebob/ub-mode | 24 | 0% | 12% | 20.0 | 6.1 |
| sickn33/clean-code | 24 | 0% | 8% | 18.9 | 5.9 |
| ertugrul-dmr/clean-code | 12 | 0% | 17% | 18.7 | 5.5 |
| btseee/clean-code | 12 | 8% | 8% | 21.0 | 6.2 |
| CLAUDE.md baseline | 12 | 0% | 8% | 19.8 | 6.0 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 26 | 0.06 [0.00–0.12] | 1 / 1 / 24 | 4% | 0.43 | 0.38 | 0.22 | 0.22 | 0.51 | 0.07 |
| No skill vs btseee/clean-code | 13 | 0.25 [0.04–0.48] | 3 / 0 / 10 | 0% | 0.54 | 0.40 | 0.44 | 0.29 | 0.46 | 0.40 |
| No skill vs CLAUDE.md baseline | 13 | 0.31 [0.08–0.54] | 4 / 0 / 9 | 0% | 0.62 | 0.44 | 0.38 | 0.42 | 0.50 | 0.12 |
| This repo vs unclebob/ub-mode | 26 | 1.00 [1.00–1.00] | 26 / 0 / 0 | 0% | 0.64 | 0.60 | 0.71 | 0.98 | 0.76 | 0.74 |
| This repo vs sickn33/clean-code | 26 | 0.84 [0.79–0.88] | 20 / 5 / 1 | 15% | 0.53 | 0.65 | 0.58 | 0.64 | 0.51 | 0.81 |
| This repo vs ertugrul-dmr/clean-code | 14 | 0.79 [0.68–0.89] | 9 / 4 / 1 | 7% | 0.55 | 0.55 | 0.43 | 0.70 | 0.57 | 0.75 |
| This repo vs btseee/clean-code | 13 | 0.90 [0.79–1.00] | 11 / 2 / 0 | 8% | 0.60 | 0.50 | 0.69 | 0.62 | 0.54 | 0.85 |
| This repo vs CLAUDE.md baseline | 13 | 0.73 [0.50–0.92] | 9 / 1 / 3 | 8% | 0.63 | 0.62 | 0.75 | 0.60 | 0.54 | 0.54 |

#### Checks by case (passed / runs)

**dev: Add a feature that needs helpers from other modules (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| reuses_helpers | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_reimplemented_money_logic | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| test_added | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 1/1 | 1/1 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| verified | 0/3 | 3/3 | 3/3 | 1/3 | 0/3 | 1/1 | 1/1 |

**dev: Bugfix in a legacy module with a sibling bug (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| regression_test | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 1/1 | 1/1 |
| sibling_bug | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| verified | 0/3 | 3/3 | 3/3 | 0/3 | 1/3 | 1/1 | 1/1 |

**dev: Refactor untested code with many callers (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| callers_compatible | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| any_replaced | 0/3 | 3/3 | 2/3 | 0/3 | 3/3 | 0/1 | 0/1 |
| magic_numbers_named | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 | 1/1 | 0/1 |
| characterization_tests | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/1 | 1/1 |
| no_over_engineering | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| verified | 0/3 | 3/3 | 3/3 | 0/3 | 2/3 | 1/1 | 1/1 |

**dev: Cleaning up an unreadable report module (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| output_unchanged | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| exports_and_callers_intact | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| only_expected_files_changed | 3/3 | 3/3 | 2/3 | 3/3 | 1/1 | 1/1 |
| callers_untouched | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_function_longer_than_forty_lines | 0/3 | 3/3 | 2/3 | 3/3 | 1/1 | 0/1 |
| regional_copies_consolidated | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 0/1 |
| magic_numbers_named | 2/3 | 3/3 | 1/3 | 3/3 | 1/1 | 0/1 |
| dead_code_removed | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| characterization_tests_added | 0/3 | 3/3 | 2/3 | 0/3 | 0/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/3 | 3/3 | 2/3 | 3/3 | 1/1 | 1/1 |

**dev: Student discount next to the loyalty discount (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| student_discount_applies | 2/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| larger_discount_wins_without_stacking | 2/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| existing_behavior_unchanged | 2/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| test_suite_passes | 2/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| student_tests_added | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_new_abstraction_layers | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| money_stays_bigdecimal_with_one_rounding | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| price_calculation_not_duplicated | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |

**dev: Retrying a flaky carrier API (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| transient_failures_are_retried | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| permanent_errors_are_not_retried | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| gives_up_and_keeps_the_original_error | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| keyed_create_is_retried_safely | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| unsafe_posts_are_not_repeated | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| waiting_is_injectable_and_never_real_in_tests | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| no_new_catch_all_that_swallows | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| only_expected_files_changed_and_no_new_dependency | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| regression_tests_fail_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| tests_run_after_last_edit | 3/3 | 2/3 | 2/3 | 3/3 | 3/3 | 1/1 | 1/1 |

**dev: Tests for the untested rates module (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| rates_tests_added_where_runner_finds_them | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| new_tests_pass_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| tests_catch_mutants_of_rates | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| source_code_unchanged | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| only_test_files_changed | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 | 1/1 |

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| shares_add_up | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| invalid_input_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| equal_split_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_float_money | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| readme_updated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 2/2 | 2/2 | 1/2 | 2/2 | 1/2 | 1/1 | 1/1 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| blank_lines_skipped | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| malformed_lines_still_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_catch_all_handler | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| regression_test_added | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| flag_is_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| other_behavior_preserved | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| builds_without_warnings | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_leftovers | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| other_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| changelog_entry | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Refund command for the order service (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| refund_follows_business_rules | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| refund_rejects_bad_input | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| refund_money_is_exact | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| new_tests_cover_refund | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| handler_follows_the_pattern | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| money_stays_decimal | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_console_output | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Invoice export crashes for some customers (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| customers_of_both_systems_get_their_own_name | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unknown_customer_still_fails_loudly | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unknown_customer_error_names_the_customer | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| export_format_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_guard_at_the_crash_site | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| regression_test_fails_on_original_code | 1/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 1/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Reviewing a pull request (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| finds_the_sql_injection | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| finds_the_wrong_page_count | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| finds_the_swallowed_audit_error | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| findings_cite_file_and_line | 1/2 | 2/2 | 1/2 | 2/2 | 2/2 | 0/1 | 1/1 |
| decoy_not_reported_as_bug | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| injection_before_style_remarks | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| does_not_approve | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_review_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| pr_not_left_applied | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| looked_at_the_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Adding a subscription pause event (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| reducer_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| audit_log_records_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| notifier_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| exhaustiveness_guard_kept | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_type_escape_hatches | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| event_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_the_requested_event_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 1/2 | 2/2 | 0/2 | 2/2 | 2/2 | 1/1 | 0/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_cover_all_three_sites | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Cleaning up a hot-path tokenizer (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| token_stream_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| public_api_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tokenizing_does_not_allocate | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_allocating_code_in_tokenizer | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| functions_are_short | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| blank_test_not_repeated | 2/2 | 1/2 | 1/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clippy_clean | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_edit | 1/2 | 2/2 | 2/2 | 2/2 | 0/1 | 1/1 |

**test: Making configuration errors visible (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| malformed_values_fail_naming_key_and_value | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| missing_required_keys_and_unreadable_file_fail | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| optional_keys_and_valid_files_unchanged | 1/2 | 0/2 | 0/2 | 0/2 | 0/1 | 0/1 |
| entry_point_refuses_to_start_cleanly | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_swallowing_catch_in_config_package | 1/2 | 1/2 | 0/2 | 2/2 | 0/1 | 1/1 |
| caught_exceptions_keep_their_cause | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_exit_outside_the_entry_point | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_assert_the_new_failures | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 1/2 | 0/2 | 2/2 | 1/1 | 1/1 |

**test: Pulling the user validation into one place (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|
| create_behavior_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| update_stays_partial | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| invite_keeps_its_differences | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unrelated_handlers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| email_drift_handled | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| validation_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 0/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_new_dependency | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_added_not_loosened | 0/2 | 2/2 | 2/2 | 0/2 | 0/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| parser_returns_milliseconds | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| timing_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| unit_sensitive_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| doc_comment_states_new_unit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| same_result_as_before | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| inputs_not_modified | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| work_grows_linearly | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_second_normalization | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 1/2 | 2/2 | 2/2 | 2/2 | 0/2 | 1/1 | 1/1 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code | btseee/clean-code | CLAUDE.md baseline |
|---|---|---|---|---|---|---|---|
| totals_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| failures_and_side_effects_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| new_tests_pass_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| no_function_longer_than_thirty_lines | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| public_interface_and_refund_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 1/1 |

#### Installed, nothing mentions it (the agent decides whether to load the skill)

| Condition | Runs | Runs that loaded the skill | Checks passed |
|---|---|---|---|
| This repo | 13 | 85% | 96% |
| unclebob/ub-mode | 13 | 0% | 96% |
| sickn33/clean-code | 13 | 0% | 99% |
| ertugrul-dmr/clean-code | 7 | 14% | 99% |
| btseee/clean-code | 13 | 8% | 95% |

#### Installed, with the CLAUDE.md line that asks the agent to load it

| Condition | Runs | Runs that loaded the skill | Checks passed |
|---|---|---|---|
| This repo | 13 | 100% | 97% |
| unclebob/ub-mode | 13 | 100% | 95% |
| sickn33/clean-code | 13 | 100% | 97% |
| ertugrul-dmr/clean-code | 7 | 100% | 97% |
| btseee/clean-code | 13 | 100% | 99% |
