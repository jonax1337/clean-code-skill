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

/// Streams the tokens of one line. After the first error it yields nothing more.
#[derive(Debug, Clone)]
pub struct Tokens<'a> {
    src: &'a str,
    pos: usize,
    st: u8,
}

impl<'a> Tokens<'a> {
    pub fn new(src: &'a str) -> Self {
        Tokens { src, pos: 0, st: 0 }
    }
}

/// Tokenizes one log line without copying any of it.
pub fn tokenize(line: &str) -> Tokens<'_> {
    Tokens::new(line)
}

impl<'a> Iterator for Tokens<'a> {
    type Item = Result<Token<'a>, LexError>;

    fn next(&mut self) -> Option<Self::Item> {
        let src: &'a str = self.src;
        let b = src.as_bytes();
        let n = b.len();
        let mut p = self.pos;
        match self.st {
            0 => {
                while p < n && (b[p] == b' ' || b[p] == b'\t') {
                    p += 1;
                }
                if p >= n {
                    self.pos = p;
                    return None;
                }
                match b[p] {
                    b'[' => {
                        let s = p + 1;
                        let mut i = s;
                        loop {
                            if i >= n {
                                self.st = 2;
                                self.pos = n;
                                return Some(Err(LexError::UnterminatedTimestamp { pos: p }));
                            }
                            match b[i] {
                                b']' => break,
                                b'[' => {
                                    self.st = 2;
                                    self.pos = n;
                                    return Some(Err(LexError::NestedBracket { pos: i }));
                                }
                                _ => i += 1,
                            }
                        }
                        if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
                            self.st = 2;
                            self.pos = n;
                            return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
                        }
                        self.pos = i + 1;
                        Some(Ok(Token::Timestamp(&src[s..i])))
                    }
                    b'"' => {
                        self.st = 2;
                        self.pos = n;
                        Some(Err(LexError::UnexpectedQuote { pos: p }))
                    }
                    b'=' => {
                        self.st = 2;
                        self.pos = n;
                        Some(Err(LexError::EmptyKey { pos: p }))
                    }
                    _ => {
                        let mut i = p;
                        while i < n && b[i] != b' ' && b[i] != b'\t' && b[i] != b'=' {
                            if b[i] == b'"' {
                                self.st = 2;
                                self.pos = n;
                                return Some(Err(LexError::UnexpectedQuote { pos: i }));
                            }
                            i += 1;
                        }
                        if i < n && b[i] == b'=' {
                            self.st = 1;
                            self.pos = i + 1;
                            Some(Ok(Token::Key(&src[p..i])))
                        } else {
                            self.pos = i;
                            Some(Ok(Token::Word(&src[p..i])))
                        }
                    }
                }
            }
            1 => {
                if p >= n || b[p] == b' ' || b[p] == b'\t' {
                    self.st = 0;
                    self.pos = p;
                    return Some(Ok(Token::Bare(&src[p..p])));
                }
                if b[p] == b'"' {
                    let s = p + 1;
                    let mut i = s;
                    loop {
                        if i >= n {
                            self.st = 2;
                            self.pos = n;
                            return Some(Err(LexError::UnterminatedQuote { pos: p }));
                        }
                        match b[i] {
                            b'"' => break,
                            b'\\' => {
                                if i + 1 >= n {
                                    self.st = 2;
                                    self.pos = n;
                                    return Some(Err(LexError::UnterminatedQuote { pos: p }));
                                }
                                match b[i + 1] {
                                    b'"' | b'\\' | b'n' | b't' => i += 2,
                                    _ => {
                                        self.st = 2;
                                        self.pos = n;
                                        return Some(Err(LexError::InvalidEscape { pos: i }));
                                    }
                                }
                            }
                            _ => i += 1,
                        }
                    }
                    if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
                        self.st = 2;
                        self.pos = n;
                        return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
                    }
                    self.st = 0;
                    self.pos = i + 1;
                    Some(Ok(Token::Quoted(&src[s..i])))
                } else {
                    let mut i = p;
                    while i < n && b[i] != b' ' && b[i] != b'\t' {
                        if b[i] == b'"' {
                            self.st = 2;
                            self.pos = n;
                            return Some(Err(LexError::UnexpectedQuote { pos: i }));
                        }
                        i += 1;
                    }
                    self.st = 0;
                    self.pos = i;
                    Some(Ok(Token::Bare(&src[p..i])))
                }
            }
            _ => None,
        }
    }
}
