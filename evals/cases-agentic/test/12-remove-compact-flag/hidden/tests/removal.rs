use tabulate::{run, CliError};

const PEOPLE: &str = "id,name,city\n7,Ann,Oslo\n10,Bob,Rome\n";

fn assert_unknown_option(args: &[&str]) {
    match run(args, PEOPLE) {
        Err(CliError::UnknownOption(option)) => {
            assert!(
                args.contains(&option.as_str()),
                "reported {option:?}, expected one of {args:?}"
            );
        }
        other => panic!("{args:?} should be an unknown option, got {other:?}"),
    }
}

#[test]
fn removed_long_flag_is_an_unknown_option() {
    assert_unknown_option(&["--compact"]);
}

#[test]
fn removed_short_flag_is_an_unknown_option() {
    assert_unknown_option(&["-c"]);
}

#[test]
fn removed_flag_is_rejected_between_other_options() {
    assert_unknown_option(&["--header", "--compact", "--border"]);
    assert_unknown_option(&["-H", "-c", "-w", "5"]);
}

#[test]
fn removed_flag_is_not_advertised_in_the_help() {
    let help = run(&["--help"], "").unwrap();
    assert!(!help.to_lowercase().contains("compact"), "help still mentions it:\n{help}");
    assert!(!help.contains("-c,"), "help still lists -c:\n{help}");
}

#[test]
fn preserved_default_output() {
    assert_eq!(
        run(&[], PEOPLE).unwrap(),
        "id  name  city\n7   Ann   Oslo\n10  Bob   Rome\n"
    );
}

#[test]
fn preserved_header_and_border() {
    assert_eq!(
        run(&["--header", "--border"], PEOPLE).unwrap(),
        "| id | name | city |\n|----+------+------|\n| 7  | Ann  | Oslo |\n| 10 | Bob  | Rome |\n"
    );
}

#[test]
fn preserved_delimiter_and_ragged_rows() {
    assert_eq!(
        run(&["-d", "tab"], "a\tbb\tc\nd\n").unwrap(),
        "a  bb  c\nd\n"
    );
}

#[test]
fn preserved_max_width_truncation() {
    assert_eq!(
        run(&["--max-width", "4"], "abcdef,xy\n").unwrap(),
        "abc…  xy\n"
    );
    assert_eq!(
        run(&["-w", "4", "-b"], "abcdef,xy\n").unwrap(),
        "| abc… | xy |\n"
    );
}

#[test]
fn preserved_errors_for_other_bad_arguments() {
    assert_eq!(
        run(&["--nope"], PEOPLE),
        Err(CliError::UnknownOption("--nope".to_string()))
    );
    assert_eq!(
        run(&["-w"], PEOPLE),
        Err(CliError::MissingValue("-w".to_string()))
    );
    assert_eq!(
        run(&["-w", "x"], PEOPLE),
        Err(CliError::InvalidValue {
            option: "-w".to_string(),
            value: "x".to_string()
        })
    );
}

#[test]
fn preserved_help_text() {
    let help = run(&["-h"], "").unwrap();
    for option in ["--delimiter", "--header", "--border", "--max-width", "--help"] {
        assert!(help.contains(option), "help does not mention {option}");
    }
}
