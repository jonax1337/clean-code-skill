# Agentic eval results

A coding agent with Read/Grep/Glob/Edit/Write/Bash works on a fresh copy of a fixture repo; deterministic
checks grade the result and a blind judge compares runs pairwise. `dev` cases may have shaped the skill;
`test` cases are held out. Cases are weighted equally. Brackets are 95 % bootstrap intervals that resample
runs within each case, so they describe these cases only.

## Coder: haiku

### test cases (13)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 26 | 96% [95%–97%] | – | -1 pts [-2 to +1] | 16/26 | $0.010 | 15.0 |
| This repo | 26 | 96% [95%–97%] | +1 pts [-1 to +2] | – | 18/26 | $0.015 | 15.8 |
| unclebob/ub-mode | 26 | 97% [96%–98%] | +2 pts [+0 to +3] | +1 pts [-1 to +2] | 21/26 | $0.014 | 17.0 |
| sickn33/clean-code | 26 | 95% [93%–96%] | -1 pts [-3 to +0] | -2 pts [-4 to -0] | 15/26 | $0.010 | 13.9 |
| ertugrul-dmr/clean-code | 14 | 96% [94%–98%] | – | – | 9/14 | $0.008 | 12.9 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 24 | 0% | 8% | 21.1 | 6.5 |
| This repo | 24 | 4% | 8% | 21.2 | 6.5 |
| unclebob/ub-mode | 24 | 0% | 8% | 20.1 | 5.9 |
| sickn33/clean-code | 24 | 0% | 8% | 20.5 | 6.3 |
| ertugrul-dmr/clean-code | 12 | 0% | 17% | 20.3 | 5.5 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 26 | 0.46 [0.35–0.58] | 11 / 2 / 13 | 4% | 0.54 | 0.54 | 0.50 | 0.39 | 0.52 | 0.38 |
| This repo vs unclebob/ub-mode | 26 | 0.46 [0.35–0.58] | 11 / 2 / 13 | 8% | 0.51 | 0.45 | 0.53 | 0.63 | 0.55 | 0.44 |
| This repo vs sickn33/clean-code | 26 | 0.63 [0.54–0.73] | 14 / 6 / 6 | 23% | 0.56 | 0.61 | 0.53 | 0.51 | 0.50 | 0.62 |
| This repo vs ertugrul-dmr/clean-code | 14 | 0.75 [0.57–0.93] | 10 / 1 / 3 | 7% | 0.46 | 0.59 | 0.64 | 0.68 | 0.50 | 0.64 |

#### Checks by case (passed / runs)

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| shares_add_up | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| invalid_input_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| equal_split_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_float_money | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| readme_updated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 1/2 | 1/2 | 2/2 | 1/2 | 1/2 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| blank_lines_skipped | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| malformed_lines_still_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_catch_all_handler | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 1/2 | 2/2 | 1/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| flag_is_rejected | 2/2 | 2/2 | 2/2 | 2/2 |
| other_behavior_preserved | 2/2 | 2/2 | 2/2 | 2/2 |
| builds_without_warnings | 2/2 | 2/2 | 2/2 | 2/2 |
| no_leftovers | 2/2 | 2/2 | 2/2 | 2/2 |
| other_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| changelog_entry | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Refund command for the order service (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| refund_follows_business_rules | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_rejects_bad_input | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_money_is_exact | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_cover_refund | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| handler_follows_the_pattern | 2/2 | 2/2 | 2/2 | 2/2 |
| money_stays_decimal | 2/2 | 2/2 | 2/2 | 2/2 |
| no_console_output | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 1/2 | 2/2 | 2/2 |

**test: Invoice export crashes for some customers (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| customers_of_both_systems_get_their_own_name | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_still_fails_loudly | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_error_names_the_customer | 2/2 | 2/2 | 2/2 | 1/2 |
| export_format_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| no_guard_at_the_crash_site | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_fails_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Reviewing a pull request (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| finds_the_sql_injection | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_wrong_page_count | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_swallowed_audit_error | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| findings_cite_file_and_line | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| decoy_not_reported_as_bug | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| injection_before_style_remarks | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| does_not_approve | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_review_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| pr_not_left_applied | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| looked_at_the_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Adding a subscription pause event (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| reducer_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| audit_log_records_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| notifier_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| exhaustiveness_guard_kept | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_type_escape_hatches | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| event_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_the_requested_event_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 1/2 | 1/2 | 2/2 | 2/2 | 1/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_cover_all_three_sites | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Cleaning up a hot-path tokenizer (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| token_stream_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| public_api_unchanged | 2/2 | 2/2 | 2/2 | 1/2 |
| tokenizing_does_not_allocate | 2/2 | 2/2 | 2/2 | 2/2 |
| no_allocating_code_in_tokenizer | 2/2 | 2/2 | 2/2 | 2/2 |
| functions_are_short | 2/2 | 2/2 | 2/2 | 2/2 |
| blank_test_not_repeated | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| clippy_clean | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 1/2 | 2/2 | 1/2 | 2/2 |

**test: Making configuration errors visible (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| malformed_values_fail_naming_key_and_value | 2/2 | 2/2 | 2/2 | 2/2 |
| missing_required_keys_and_unreadable_file_fail | 2/2 | 2/2 | 2/2 | 2/2 |
| optional_keys_and_valid_files_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| entry_point_refuses_to_start_cleanly | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_swallowing_catch_in_config_package | 1/2 | 1/2 | 1/2 | 0/2 |
| caught_exceptions_keep_their_cause | 1/2 | 0/2 | 0/2 | 0/2 |
| no_exit_outside_the_entry_point | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_assert_the_new_failures | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 0/2 | 0/2 | 0/2 | 0/2 |

**test: Pulling the user validation into one place (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| create_behavior_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| update_stays_partial | 2/2 | 2/2 | 2/2 | 2/2 |
| invite_keeps_its_differences | 2/2 | 2/2 | 2/2 | 2/2 |
| unrelated_handlers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| email_drift_handled | 2/2 | 2/2 | 2/2 | 2/2 |
| validation_defined_once | 2/2 | 1/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_new_dependency | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added_not_loosened | 2/2 | 2/2 | 2/2 | 0/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 1/2 | 1/2 | 1/2 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| parser_returns_milliseconds | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| timing_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| unit_sensitive_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 1/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| doc_comment_states_new_unit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| same_result_as_before | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| inputs_not_modified | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| work_grows_linearly | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_second_normalization | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 0/2 | 1/2 | 2/2 | 0/2 | 0/2 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| totals_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| failures_and_side_effects_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_pass_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_function_longer_than_thirty_lines | 2/2 | 2/2 | 2/2 | 2/2 | 1/2 |
| public_interface_and_refund_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 0/2 | 2/2 | 2/2 | 1/2 | 1/2 |

## Coder: opus

### test cases (13)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 26 | 97% [96%–98%] | – | -1 pts [-2 to +1] | 19/26 | $0.244 | 10.3 |
| This repo | 26 | 98% [97%–99%] | +1 pts [-1 to +2] | – | 21/26 | $0.329 | 10.5 |
| unclebob/ub-mode | 26 | 94% [93%–95%] | -3 pts [-5 to -1] | -3 pts [-5 to -2] | 15/26 | $0.358 | 12.1 |
| sickn33/clean-code | 26 | 99% [98%–99%] | +2 pts [+1 to +3] | +1 pts [+0 to +2] | 23/26 | $0.264 | 11.1 |
| ertugrul-dmr/clean-code | 14 | 99% [99%–100%] | – | – | 13/14 | $0.229 | 8.1 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 24 | 0% | 8% | 19.7 | 6.1 |
| This repo | 24 | 0% | 8% | 19.0 | 5.8 |
| unclebob/ub-mode | 24 | 0% | 8% | 18.6 | 5.6 |
| sickn33/clean-code | 24 | 0% | 8% | 17.2 | 5.4 |
| ertugrul-dmr/clean-code | 12 | 0% | 17% | 18.9 | 5.6 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 26 | 0.29 [0.23–0.35] | 7 / 1 / 18 | 0% | 0.47 | 0.48 | 0.58 | 0.24 | 0.46 | 0.30 |
| This repo vs unclebob/ub-mode | 26 | 0.81 [0.75–0.87] | 19 / 4 / 3 | 15% | 0.49 | 0.50 | 0.54 | 0.89 | 0.78 | 0.46 |
| This repo vs sickn33/clean-code | 26 | 0.74 [0.64–0.84] | 18 / 3 / 5 | 12% | 0.55 | 0.50 | 0.47 | 0.69 | 0.55 | 0.72 |
| This repo vs ertugrul-dmr/clean-code | 14 | 0.59 [0.46–0.71] | 7 / 3 / 4 | 14% | 0.43 | 0.41 | 0.48 | 0.68 | 0.59 | 0.50 |

#### Checks by case (passed / runs)

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| shares_add_up | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| invalid_input_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| equal_split_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_float_money | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| readme_updated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 1/2 | 2/2 | 0/2 | 2/2 | 2/2 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| blank_lines_skipped | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| malformed_lines_still_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_catch_all_handler | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 0/2 | 0/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 1/2 | 2/2 | 2/2 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| flag_is_rejected | 2/2 | 2/2 | 2/2 | 2/2 |
| other_behavior_preserved | 2/2 | 2/2 | 2/2 | 2/2 |
| builds_without_warnings | 2/2 | 2/2 | 2/2 | 2/2 |
| no_leftovers | 2/2 | 2/2 | 2/2 | 2/2 |
| other_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| changelog_entry | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Refund command for the order service (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| refund_follows_business_rules | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_rejects_bad_input | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_money_is_exact | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_cover_refund | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| handler_follows_the_pattern | 2/2 | 2/2 | 2/2 | 2/2 |
| money_stays_decimal | 2/2 | 2/2 | 2/2 | 2/2 |
| no_console_output | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Invoice export crashes for some customers (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| customers_of_both_systems_get_their_own_name | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_still_fails_loudly | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_error_names_the_customer | 2/2 | 2/2 | 2/2 | 2/2 |
| export_format_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| no_guard_at_the_crash_site | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_fails_on_original_code | 1/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Reviewing a pull request (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| finds_the_sql_injection | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_wrong_page_count | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_swallowed_audit_error | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| findings_cite_file_and_line | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| decoy_not_reported_as_bug | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| injection_before_style_remarks | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| does_not_approve | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_review_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| pr_not_left_applied | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| looked_at_the_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Adding a subscription pause event (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| reducer_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| audit_log_records_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| notifier_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| exhaustiveness_guard_kept | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_type_escape_hatches | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| event_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_the_requested_event_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_cover_all_three_sites | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Cleaning up a hot-path tokenizer (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| token_stream_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| public_api_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| tokenizing_does_not_allocate | 2/2 | 2/2 | 2/2 | 2/2 |
| no_allocating_code_in_tokenizer | 2/2 | 2/2 | 2/2 | 2/2 |
| functions_are_short | 2/2 | 2/2 | 2/2 | 2/2 |
| blank_test_not_repeated | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 1/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| clippy_clean | 2/2 | 2/2 | 1/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 1/2 | 2/2 |
| tests_run_after_edit | 2/2 | 1/2 | 0/2 | 2/2 |

**test: Making configuration errors visible (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| malformed_values_fail_naming_key_and_value | 2/2 | 2/2 | 2/2 | 2/2 |
| missing_required_keys_and_unreadable_file_fail | 2/2 | 2/2 | 2/2 | 2/2 |
| optional_keys_and_valid_files_unchanged | 2/2 | 1/2 | 2/2 | 2/2 |
| entry_point_refuses_to_start_cleanly | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_swallowing_catch_in_config_package | 2/2 | 1/2 | 0/2 | 0/2 |
| caught_exceptions_keep_their_cause | 0/2 | 2/2 | 2/2 | 2/2 |
| no_exit_outside_the_entry_point | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_assert_the_new_failures | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 0/2 | 0/2 | 0/2 | 1/2 |

**test: Pulling the user validation into one place (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| create_behavior_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| update_stays_partial | 2/2 | 2/2 | 2/2 | 2/2 |
| invite_keeps_its_differences | 2/2 | 2/2 | 2/2 | 2/2 |
| unrelated_handlers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| email_drift_handled | 2/2 | 2/2 | 2/2 | 2/2 |
| validation_defined_once | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_new_dependency | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 1/2 | 2/2 | 0/2 | 2/2 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| parser_returns_milliseconds | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| timing_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| unit_sensitive_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| doc_comment_states_new_unit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| same_result_as_before | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| inputs_not_modified | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| work_grows_linearly | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_second_normalization | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 0/2 | 2/2 | 2/2 | 1/2 | 1/2 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| totals_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| failures_and_side_effects_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_pass_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_function_longer_than_thirty_lines | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| public_interface_and_refund_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 1/2 | 2/2 | 2/2 |

## Coder: sonnet

### dev cases (7)

| Condition | Runs | Checks passed | Δ vs No skill | Δ vs This repo | Runs passing every check | Avg. cost | Avg. turns |
|---|---|---|---|---|---|---|---|
| No skill | 21 | 82% [78%–85%] | – | -17 pts [-21 to -15] | 8/21 | $0.079 | 8.9 |
| This repo | 21 | 100% [99%–100%] | +17 pts [+15 to +21] | – | 20/21 | $0.148 | 12.2 |
| unclebob/ub-mode | 21 | 95% [92%–98%] | +13 pts [+8 to +18] | -4 pts [-8 to -2] | 15/21 | $0.097 | 8.6 |
| sickn33/clean-code | 21 | 88% [88%–89%] | +6 pts [+3 to +10] | -11 pts [-12 to -10] | 9/21 | $0.092 | 8.8 |
| ertugrul-dmr/clean-code | 15 | 89% [87%–90%] | – | – | 6/15 | $0.079 | 8.0 |

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 18 | 0% | 11% | 18.1 | 6.0 |
| This repo | 18 | 0% | 0% | 12.9 | 4.5 |
| unclebob/ub-mode | 18 | 0% | 6% | 15.7 | 5.2 |
| sickn33/clean-code | 18 | 0% | 0% | 16.3 | 5.5 |
| ertugrul-dmr/clean-code | 12 | 0% | 0% | 10.8 | 3.8 |

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

Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic
complexity above 10). Lower is better; reported, not graded.

| Condition | Runs | Runs adding a long function | Runs adding a complex function | Longest function after (lines) | Highest complexity after |
|---|---|---|---|---|---|
| No skill | 24 | 0% | 8% | 20.3 | 6.5 |
| This repo | 24 | 0% | 8% | 19.3 | 6.0 |
| unclebob/ub-mode | 24 | 0% | 12% | 20.0 | 6.1 |
| sickn33/clean-code | 24 | 0% | 8% | 18.9 | 5.9 |
| ertugrul-dmr/clean-code | 12 | 0% | 17% | 18.7 | 5.5 |

| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | correctness | design | readability | report | scope | tests |
|---|---|---|---|---|---|---|---|---|---|---|
| No skill vs This repo | 26 | 0.06 [0.00–0.12] | 1 / 1 / 24 | 4% | 0.43 | 0.38 | 0.22 | 0.22 | 0.51 | 0.07 |
| This repo vs unclebob/ub-mode | 26 | 1.00 [1.00–1.00] | 26 / 0 / 0 | 0% | 0.64 | 0.60 | 0.71 | 0.98 | 0.76 | 0.74 |
| This repo vs sickn33/clean-code | 26 | 0.84 [0.79–0.88] | 20 / 5 / 1 | 15% | 0.53 | 0.65 | 0.58 | 0.64 | 0.51 | 0.81 |
| This repo vs ertugrul-dmr/clean-code | 14 | 0.79 [0.68–0.89] | 9 / 4 / 1 | 7% | 0.55 | 0.55 | 0.43 | 0.70 | 0.57 | 0.75 |

#### Checks by case (passed / runs)

**dev: Add a feature that needs helpers from other modules (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| reuses_helpers | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_reimplemented_money_logic | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| test_added | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 3/3 | 3/3 | 1/3 | 0/3 |

**dev: Bugfix in a legacy module with a sibling bug (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_test | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| sibling_bug | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 3/3 | 3/3 | 0/3 | 1/3 |

**dev: Refactor untested code with many callers (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| callers_compatible | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| any_replaced | 0/3 | 3/3 | 2/3 | 0/3 | 3/3 |
| magic_numbers_named | 0/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| characterization_tests | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| no_over_engineering | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 3/3 | 3/3 | 0/3 | 2/3 |

**dev: Cleaning up an unreadable report module (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| output_unchanged | 3/3 | 3/3 | 3/3 | 3/3 |
| exports_and_callers_intact | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 2/3 | 3/3 |
| callers_untouched | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 |
| no_function_longer_than_forty_lines | 0/3 | 3/3 | 2/3 | 3/3 |
| regional_copies_consolidated | 3/3 | 3/3 | 3/3 | 3/3 |
| magic_numbers_named | 2/3 | 3/3 | 1/3 | 3/3 |
| dead_code_removed | 3/3 | 3/3 | 3/3 | 3/3 |
| characterization_tests_added | 0/3 | 3/3 | 2/3 | 0/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 2/3 | 3/3 | 2/3 | 3/3 |

**dev: Student discount next to the loyalty discount (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| student_discount_applies | 2/3 | 3/3 | 3/3 | 3/3 |
| larger_discount_wins_without_stacking | 2/3 | 3/3 | 3/3 | 3/3 |
| existing_behavior_unchanged | 2/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 2/3 | 3/3 | 3/3 | 3/3 |
| student_tests_added | 3/3 | 3/3 | 3/3 | 3/3 |
| no_new_abstraction_layers | 3/3 | 3/3 | 3/3 | 3/3 |
| money_stays_bigdecimal_with_one_rounding | 3/3 | 3/3 | 3/3 | 3/3 |
| price_calculation_not_duplicated | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 2/3 | 3/3 | 3/3 | 3/3 |

**dev: Retrying a flaky carrier API (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| transient_failures_are_retried | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| permanent_errors_are_not_retried | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| gives_up_and_keeps_the_original_error | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| keyed_create_is_retried_safely | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| unsafe_posts_are_not_repeated | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| waiting_is_injectable_and_never_real_in_tests | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| no_new_catch_all_that_swallows | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| only_expected_files_changed_and_no_new_dependency | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| regression_tests_fail_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 2/3 | 2/3 | 3/3 | 3/3 |

**dev: Tests for the untested rates module (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| rates_tests_added_where_runner_finds_them | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| new_tests_pass_on_original_code | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_catch_mutants_of_rates | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| source_code_unchanged | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| only_test_files_changed | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| test_suite_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| typecheck_passes | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| existing_tests_not_loosened | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| tests_run_after_last_edit | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |

**test: Split an expense by percentage (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| shares_add_up | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| invalid_input_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| equal_split_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_float_money | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| readme_updated | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 1/2 | 2/2 | 1/2 |

**test: CSV import fails on blank lines (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| blank_lines_skipped | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| malformed_lines_still_rejected | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_catch_all_handler | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_added | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Remove a deprecated CLI flag (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| flag_is_rejected | 2/2 | 2/2 | 2/2 | 2/2 |
| other_behavior_preserved | 2/2 | 2/2 | 2/2 | 2/2 |
| builds_without_warnings | 2/2 | 2/2 | 2/2 | 2/2 |
| no_leftovers | 2/2 | 2/2 | 2/2 | 2/2 |
| other_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| changelog_entry | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Refund command for the order service (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| refund_follows_business_rules | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_rejects_bad_input | 2/2 | 2/2 | 2/2 | 2/2 |
| refund_money_is_exact | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_cover_refund | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| handler_follows_the_pattern | 2/2 | 2/2 | 2/2 | 2/2 |
| money_stays_decimal | 2/2 | 2/2 | 2/2 | 2/2 |
| no_console_output | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Invoice export crashes for some customers (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| customers_of_both_systems_get_their_own_name | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_still_fails_loudly | 2/2 | 2/2 | 2/2 | 2/2 |
| unknown_customer_error_names_the_customer | 2/2 | 2/2 | 2/2 | 2/2 |
| export_format_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| no_guard_at_the_crash_site | 2/2 | 2/2 | 2/2 | 2/2 |
| regression_test_fails_on_original_code | 1/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 1/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Reviewing a pull request (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| finds_the_sql_injection | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_wrong_page_count | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| finds_the_swallowed_audit_error | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| findings_cite_file_and_line | 1/2 | 2/2 | 1/2 | 2/2 | 2/2 |
| decoy_not_reported_as_bug | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| injection_before_style_remarks | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| does_not_approve | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_review_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| pr_not_left_applied | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| looked_at_the_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Adding a subscription pause event (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| reducer_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| audit_log_records_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| notifier_handles_pause | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| exhaustiveness_guard_kept | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_type_escape_hatches | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| event_defined_once | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_the_requested_event_added | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 1/2 | 2/2 | 0/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_cover_all_three_sites | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Cleaning up a hot-path tokenizer (Rust)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| token_stream_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| public_api_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| tokenizing_does_not_allocate | 2/2 | 2/2 | 2/2 | 2/2 |
| no_allocating_code_in_tokenizer | 2/2 | 2/2 | 2/2 | 2/2 |
| functions_are_short | 2/2 | 2/2 | 2/2 | 2/2 |
| blank_test_not_repeated | 2/2 | 1/2 | 1/2 | 2/2 |
| only_expected_files | 2/2 | 2/2 | 2/2 | 2/2 |
| suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_kept | 2/2 | 2/2 | 2/2 | 2/2 |
| clippy_clean | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_edit | 1/2 | 2/2 | 2/2 | 2/2 |

**test: Making configuration errors visible (Java)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| malformed_values_fail_naming_key_and_value | 2/2 | 2/2 | 2/2 | 2/2 |
| missing_required_keys_and_unreadable_file_fail | 2/2 | 2/2 | 2/2 | 2/2 |
| optional_keys_and_valid_files_unchanged | 1/2 | 0/2 | 0/2 | 0/2 |
| entry_point_refuses_to_start_cleanly | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_swallowing_catch_in_config_package | 1/2 | 1/2 | 0/2 | 2/2 |
| caught_exceptions_keep_their_cause | 2/2 | 2/2 | 2/2 | 2/2 |
| no_exit_outside_the_entry_point | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_assert_the_new_failures | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 1/2 | 0/2 | 2/2 |

**test: Pulling the user validation into one place (JavaScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code |
|---|---|---|---|---|
| create_behavior_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| update_stays_partial | 2/2 | 2/2 | 2/2 | 2/2 |
| invite_keeps_its_differences | 2/2 | 2/2 | 2/2 | 2/2 |
| unrelated_handlers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 |
| email_drift_handled | 2/2 | 2/2 | 2/2 | 2/2 |
| validation_defined_once | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 |
| no_new_dependency | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_added_not_loosened | 0/2 | 2/2 | 2/2 | 0/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Duration parser switches from seconds to milliseconds (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| parser_returns_milliseconds | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| timing_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| unit_sensitive_callers_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| doc_comment_states_new_unit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**test: Speeding up the contact import merge (TypeScript)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| same_result_as_before | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| inputs_not_modified | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| work_grows_linearly | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| typecheck_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_second_normalization | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 1/2 | 2/2 | 2/2 | 2/2 | 0/2 |

**test: Splitting up the checkout function (Python)**

| Check | No skill | This repo | unclebob/ub-mode | sickn33/clean-code | ertugrul-dmr/clean-code |
|---|---|---|---|---|---|
| totals_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| failures_and_side_effects_unchanged | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| only_expected_files_changed | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| existing_tests_not_loosened | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| new_tests_pass_on_original_code | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| test_suite_passes | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| no_function_longer_than_thirty_lines | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| public_interface_and_refund_untouched | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| clean_diff | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| tests_run_after_last_edit | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

#### Installed, nothing mentions it (the agent decides whether to load the skill)

| Condition | Runs | Runs that loaded the skill | Checks passed |
|---|---|---|---|
| This repo | 13 | 85% | 96% |
| unclebob/ub-mode | 13 | 0% | 96% |
| sickn33/clean-code | 13 | 0% | 99% |
| ertugrul-dmr/clean-code | 7 | 14% | 99% |

#### Installed, with the CLAUDE.md line that asks the agent to load it

| Condition | Runs | Runs that loaded the skill | Checks passed |
|---|---|---|---|
| This repo | 13 | 100% | 97% |
| unclebob/ub-mode | 13 | 100% | 95% |
| sickn33/clean-code | 13 | 100% | 97% |
| ertugrul-dmr/clean-code | 7 | 100% | 97% |
