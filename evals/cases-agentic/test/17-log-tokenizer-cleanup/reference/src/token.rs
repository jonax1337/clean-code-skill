use crate::error::LexError;

/// One piece of a log line, borrowed from the line itself.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Token<'a> {
    /// The text between `[` and `]`.
    Timestamp(&'a str),
    /// The name in front of `=`.
    Key(&'a str),
    /// A double-quoted value without its quotes, escapes left as written.
    Quoted(&'a str),
    /// An unquoted value; empty for `key=` followed by a space or the end of the line.
    Bare(&'a str),
    /// A run of characters that is neither a timestamp nor part of a pair.
    Word(&'a str),
}

/// What the tokenizer expects to read next.
#[derive(Debug, Clone, Copy)]
enum State {
    /// A timestamp, a key or a word.
    Line,
    /// The value after a key's `=`.
    Value,
    /// A token was malformed; nothing more is produced.
    Failed,
}

/// Streams the tokens of one line. After the first error it yields nothing more.
#[derive(Debug, Clone)]
pub struct Tokens<'a> {
    src: &'a str,
    pos: usize,
    state: State,
}

impl<'a> Tokens<'a> {
    pub fn new(src: &'a str) -> Self {
        Tokens { src, pos: 0, state: State::Line }
    }

    fn bytes(&self) -> &'a [u8] {
        self.src.as_bytes()
    }

    fn skip_blanks(&mut self) {
        let bytes = self.bytes();
        while bytes.get(self.pos).is_some_and(|&byte| is_blank(byte)) {
            self.pos += 1;
        }
    }

    fn line_token(&mut self) -> Result<Token<'a>, LexError> {
        match self.bytes()[self.pos] {
            b'[' => self.timestamp(),
            b'"' => Err(LexError::UnexpectedQuote { pos: self.pos }),
            b'=' => Err(LexError::EmptyKey { pos: self.pos }),
            _ => self.key_or_word(),
        }
    }

    fn timestamp(&mut self) -> Result<Token<'a>, LexError> {
        let bytes = self.bytes();
        let open = self.pos;
        let start = open + 1;
        let offset = bytes[start..]
            .iter()
            .position(|&byte| byte == b']' || byte == b'[')
            .ok_or(LexError::UnterminatedTimestamp { pos: open })?;
        let end = start + offset;
        if bytes[end] == b'[' {
            return Err(LexError::NestedBracket { pos: end });
        }
        self.finish_token_at(end + 1)?;
        Ok(Token::Timestamp(&self.src[start..end]))
    }

    fn key_or_word(&mut self) -> Result<Token<'a>, LexError> {
        let bytes = self.bytes();
        let start = self.pos;
        let mut end = start;
        while let Some(&byte) = bytes.get(end) {
            match byte {
                b'=' | b' ' | b'\t' => break,
                b'"' => return Err(LexError::UnexpectedQuote { pos: end }),
                _ => end += 1,
            }
        }
        let text = &self.src[start..end];
        if bytes.get(end) == Some(&b'=') {
            self.pos = end + 1;
            self.state = State::Value;
            Ok(Token::Key(text))
        } else {
            self.pos = end;
            Ok(Token::Word(text))
        }
    }

    fn value_token(&mut self) -> Result<Token<'a>, LexError> {
        self.state = State::Line;
        match self.bytes().get(self.pos) {
            Some(b'"') => self.quoted_value(),
            _ => self.bare_value(),
        }
    }

    fn quoted_value(&mut self) -> Result<Token<'a>, LexError> {
        let bytes = self.bytes();
        let open = self.pos;
        let start = open + 1;
        let mut end = start;
        loop {
            match bytes.get(end) {
                None => return Err(LexError::UnterminatedQuote { pos: open }),
                Some(b'"') => break,
                Some(b'\\') => end = escape_end(bytes, open, end)?,
                Some(_) => end += 1,
            }
        }
        self.finish_token_at(end + 1)?;
        Ok(Token::Quoted(&self.src[start..end]))
    }

    fn bare_value(&mut self) -> Result<Token<'a>, LexError> {
        let bytes = self.bytes();
        let start = self.pos;
        let mut end = start;
        while let Some(&byte) = bytes.get(end) {
            match byte {
                b' ' | b'\t' => break,
                b'"' => return Err(LexError::UnexpectedQuote { pos: end }),
                _ => end += 1,
            }
        }
        self.pos = end;
        Ok(Token::Bare(&self.src[start..end]))
    }

    /// Moves past a token that ends just before `end`, which must be a blank or the end of the line.
    fn finish_token_at(&mut self, end: usize) -> Result<(), LexError> {
        match self.bytes().get(end) {
            Some(&byte) if !is_blank(byte) => Err(LexError::ExpectedSeparator { pos: end }),
            _ => {
                self.pos = end;
                Ok(())
            }
        }
    }
}

/// Tokenizes one log line without copying any of it.
pub fn tokenize(line: &str) -> Tokens<'_> {
    Tokens::new(line)
}

impl<'a> Iterator for Tokens<'a> {
    type Item = Result<Token<'a>, LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        let token = match self.state {
            State::Line => {
                self.skip_blanks();
                if self.pos >= self.src.len() {
                    return None;
                }
                self.line_token()
            }
            State::Value => self.value_token(),
            State::Failed => return None,
        };
        if token.is_err() {
            self.state = State::Failed;
        }
        Some(token)
    }
}

fn is_blank(byte: u8) -> bool {
    byte == b' ' || byte == b'\t'
}

/// Where the scan continues after the escape sequence that starts at the backslash at `backslash`.
fn escape_end(bytes: &[u8], quote: usize, backslash: usize) -> Result<usize, LexError> {
    match bytes.get(backslash + 1) {
        None => Err(LexError::UnterminatedQuote { pos: quote }),
        Some(b'"' | b'\\' | b'n' | b't') => Ok(backslash + 2),
        Some(_) => Err(LexError::InvalidEscape { pos: backslash }),
    }
}
