use logscan::{tokenize, LexError, Token};

fn tokens(line: &str) -> Result<Vec<Token<'_>>, LexError> {
    tokenize(line).collect()
}

#[test]
fn reads_a_typical_line() {
    assert_eq!(
        tokens("[2024-05-01T12:00:00Z] level=info msg=\"disk 91% full\" user=ann").unwrap(),
        vec![
            Token::Timestamp("2024-05-01T12:00:00Z"),
            Token::Key("level"),
            Token::Bare("info"),
            Token::Key("msg"),
            Token::Quoted("disk 91% full"),
            Token::Key("user"),
            Token::Bare("ann"),
        ]
    );
}

#[test]
fn quoted_values_keep_their_escapes() {
    assert_eq!(
        tokens(r#"msg="say \"hi\"\n""#).unwrap(),
        vec![Token::Key("msg"), Token::Quoted(r#"say \"hi\"\n"#)]
    );
}

#[test]
fn words_stand_alone() {
    assert_eq!(
        tokens("started worker-3 ok").unwrap(),
        vec![Token::Word("started"), Token::Word("worker-3"), Token::Word("ok")]
    );
}

#[test]
fn tabs_separate_tokens_like_spaces() {
    assert_eq!(
        tokens("a=1\tb=2").unwrap(),
        vec![Token::Key("a"), Token::Bare("1"), Token::Key("b"), Token::Bare("2")]
    );
}

#[test]
fn empty_line_has_no_tokens() {
    assert_eq!(tokens("").unwrap(), vec![]);
    assert_eq!(tokens("   \t ").unwrap(), vec![]);
}

#[test]
fn unterminated_quote_is_an_error() {
    assert_eq!(
        tokens("msg=\"never closed"),
        Err(LexError::UnterminatedQuote { pos: 4 })
    );
}

#[test]
fn unterminated_timestamp_is_an_error() {
    assert_eq!(
        tokens("[2024-05-01 level=info"),
        Err(LexError::UnterminatedTimestamp { pos: 0 })
    );
}

#[test]
fn iteration_stops_after_an_error() {
    let mut stream = tokenize("ok =bad later=1");
    assert_eq!(stream.next(), Some(Ok(Token::Word("ok"))));
    assert_eq!(stream.next(), Some(Err(LexError::EmptyKey { pos: 3 })));
    assert_eq!(stream.next(), None);
}
