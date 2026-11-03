use tabulate::{run, CliError};

const PEOPLE: &str = "id,name,city\n7,Ann,Oslo\n10,Bob,Rome\n";

#[test]
fn default_output_is_aligned() {
    assert_eq!(
        run(&[], PEOPLE).unwrap(),
        "id  name  city\n7   Ann   Oslo\n10  Bob   Rome\n"
    );
}

#[test]
fn header_is_underlined() {
    assert_eq!(
        run(&["--header"], PEOPLE).unwrap(),
        "id  name  city\n--  ----  ----\n7   Ann   Oslo\n10  Bob   Rome\n"
    );
}

#[test]
fn border_draws_pipes() {
    assert_eq!(
        run(&["-b", "-H"], "a,b\nccc,d\n").unwrap(),
        "| a   | b |\n|-----+---|\n| ccc | d |\n"
    );
}

#[test]
fn custom_delimiter_splits_cells() {
    assert_eq!(run(&["-d", ";"], "a;bb\nc;d\n").unwrap(), "a  bb\nc  d\n");
}

#[test]
fn tab_delimiter_is_spelled_out() {
    assert_eq!(run(&["-d", "tab"], "a\tbb\n").unwrap(), "a  bb\n");
}

#[test]
fn max_width_truncates_long_cells() {
    assert_eq!(run(&["-w", "3"], "abcdef,x\n").unwrap(), "ab…  x\n");
}

#[test]
fn ragged_rows_are_padded() {
    assert_eq!(run(&[], "a,b,c\nd\n").unwrap(), "a  b  c\nd\n");
}

#[test]
fn empty_input_prints_nothing() {
    assert_eq!(run(&[], "").unwrap(), "");
}

#[test]
fn unknown_option_is_rejected() {
    assert_eq!(
        run(&["--nope"], PEOPLE),
        Err(CliError::UnknownOption("--nope".to_string()))
    );
}

#[test]
fn missing_value_is_reported() {
    assert_eq!(
        run(&["-w"], PEOPLE),
        Err(CliError::MissingValue("-w".to_string()))
    );
}

#[test]
fn help_lists_every_option() {
    let help = run(&["--help"], "").unwrap();
    for option in ["--delimiter", "--header", "--border", "--max-width", "--help"] {
        assert!(help.contains(option), "help does not mention {option}");
    }
}

#[test]
fn compact_flag_is_no_longer_accepted() {
    for flag in ["--compact", "-c"] {
        assert_eq!(
            run(&[flag], PEOPLE),
            Err(CliError::UnknownOption(flag.to_string()))
        );
    }
}
