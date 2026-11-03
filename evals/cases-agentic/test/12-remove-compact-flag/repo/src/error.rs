use std::fmt;

#[derive(Debug, PartialEq, Eq)]
pub enum CliError {
    UnknownOption(String),
    MissingValue(String),
    InvalidValue { option: String, value: String },
}

impl fmt::Display for CliError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CliError::UnknownOption(option) => write!(f, "unknown option `{option}`"),
            CliError::MissingValue(option) => write!(f, "option `{option}` needs a value"),
            CliError::InvalidValue { option, value } => {
                write!(f, "invalid value `{value}` for option `{option}`")
            }
        }
    }
}

impl std::error::Error for CliError {}
