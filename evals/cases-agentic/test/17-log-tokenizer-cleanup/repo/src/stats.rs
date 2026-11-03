use crate::token::{tokenize, Token};

/// What a log dump contained, summed over all lines added so far.
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct Stats {
    pub lines: u64,
    pub rejected_lines: u64,
    pub timestamps: u64,
    pub pairs: u64,
    pub words: u64,
}

impl Stats {
    /// Counts the tokens of one line. A line with a malformed token counts as rejected from that token on.
    pub fn add_line(&mut self, line: &str) {
        self.lines += 1;
        for token in tokenize(line) {
            match token {
                Ok(Token::Timestamp(_)) => self.timestamps += 1,
                Ok(Token::Key(_)) => self.pairs += 1,
                Ok(Token::Word(_)) => self.words += 1,
                Ok(Token::Quoted(_) | Token::Bare(_)) => {}
                Err(_) => {
                    self.rejected_lines += 1;
                    break;
                }
            }
        }
    }
}
