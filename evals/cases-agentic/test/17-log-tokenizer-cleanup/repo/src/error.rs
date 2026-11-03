use std::fmt;

/// Why a line could not be tokenized; `pos` is a byte offset into the line.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LexError {
    UnterminatedTimestamp { pos: usize },
    NestedBracket { pos: usize },
    UnterminatedQuote { pos: usize },
    InvalidEscape { pos: usize },
    UnexpectedQuote { pos: usize },
    EmptyKey { pos: usize },
    ExpectedSeparator { pos: usize },
}

impl fmt::Display for LexError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            LexError::UnterminatedTimestamp { pos } => write!(f, "timestamp at {pos} is never closed"),
            LexError::NestedBracket { pos } => write!(f, "unexpected `[` inside a timestamp at {pos}"),
            LexError::UnterminatedQuote { pos } => write!(f, "quoted value at {pos} is never closed"),
            LexError::InvalidEscape { pos } => write!(f, "unknown escape sequence at {pos}"),
            LexError::UnexpectedQuote { pos } => write!(f, "unexpected `\"` at {pos}"),
            LexError::EmptyKey { pos } => write!(f, "missing key before `=` at {pos}"),
            LexError::ExpectedSeparator { pos } => write!(f, "expected a space or tab at {pos}"),
        }
    }
}

impl std::error::Error for LexError {}
