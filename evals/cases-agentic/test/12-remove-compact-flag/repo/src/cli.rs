use crate::error::CliError;

pub const USAGE: &str = "\
Usage: tabulate [OPTIONS] < input

Aligns delimited text from stdin into a plain-text table.

Options:
  -d, --delimiter <CHAR>   Cell delimiter, or `tab` (default: ,)
  -H, --header             Underline the first row
  -b, --border             Draw `|` between the columns
  -w, --max-width <N>      Cut cells longer than N characters
  -c, --compact            Deprecated: print rows without padding
  -h, --help               Show this help
";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Options {
    pub delimiter: char,
    pub header: bool,
    pub border: bool,
    pub compact: bool,
    pub max_width: Option<usize>,
}

impl Default for Options {
    fn default() -> Self {
        Options {
            delimiter: ',',
            header: false,
            border: false,
            compact: false,
            max_width: None,
        }
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum Command {
    Help,
    Render(Options),
}

pub fn parse_args(args: &[&str]) -> Result<Command, CliError> {
    let mut options = Options::default();
    let mut args = args.iter().copied();
    while let Some(arg) = args.next() {
        match arg {
            "-h" | "--help" => return Ok(Command::Help),
            "-H" | "--header" => options.header = true,
            "-b" | "--border" => options.border = true,
            "-c" | "--compact" => {
                eprintln!("warning: --compact is deprecated and will be removed in 1.0; use --max-width instead");
                options.compact = true;
            }
            "-d" | "--delimiter" => options.delimiter = parse_delimiter(arg, args.next())?,
            "-w" | "--max-width" => options.max_width = Some(parse_width(arg, args.next())?),
            other => return Err(CliError::UnknownOption(other.to_string())),
        }
    }
    Ok(Command::Render(options))
}

fn parse_delimiter(option: &str, value: Option<&str>) -> Result<char, CliError> {
    let value = value.ok_or_else(|| CliError::MissingValue(option.to_string()))?;
    if value == "tab" {
        return Ok('\t');
    }
    let mut chars = value.chars();
    match (chars.next(), chars.next()) {
        (Some(delimiter), None) => Ok(delimiter),
        _ => Err(invalid_value(option, value)),
    }
}

fn parse_width(option: &str, value: Option<&str>) -> Result<usize, CliError> {
    let value = value.ok_or_else(|| CliError::MissingValue(option.to_string()))?;
    match value.parse::<usize>() {
        Ok(width) if width > 0 => Ok(width),
        _ => Err(invalid_value(option, value)),
    }
}

fn invalid_value(option: &str, value: &str) -> CliError {
    CliError::InvalidValue {
        option: option.to_string(),
        value: value.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn options(args: &[&str]) -> Options {
        match parse_args(args) {
            Ok(Command::Render(options)) => options,
            other => panic!("expected options, got {other:?}"),
        }
    }

    #[test]
    fn defaults_apply_without_arguments() {
        assert_eq!(options(&[]), Options::default());
    }

    #[test]
    fn parses_short_and_long_flags() {
        assert!(options(&["-H"]).header);
        assert!(options(&["--border"]).border);
    }

    #[test]
    fn parses_option_values() {
        let parsed = options(&["-d", "tab", "--max-width", "8"]);
        assert_eq!(parsed.delimiter, '\t');
        assert_eq!(parsed.max_width, Some(8));
    }

    #[test]
    fn compact_flag_sets_compact() {
        assert!(options(&["--compact"]).compact);
        assert!(options(&["-c"]).compact);
    }

    #[test]
    fn rejects_unknown_options() {
        assert_eq!(
            parse_args(&["--nope"]),
            Err(CliError::UnknownOption("--nope".to_string()))
        );
    }

    #[test]
    fn rejects_a_missing_value() {
        assert_eq!(
            parse_args(&["--delimiter"]),
            Err(CliError::MissingValue("--delimiter".to_string()))
        );
    }

    #[test]
    fn rejects_a_zero_width() {
        assert!(parse_args(&["-w", "0"]).is_err());
    }
}
