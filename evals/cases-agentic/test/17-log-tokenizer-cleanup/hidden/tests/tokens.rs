//! Pins the exact token stream, including the error, for the edge cases of the line format.

use logscan::{tokenize, LexError, Token};

type Item<'a> = Result<Token<'a>, LexError>;

fn stream(line: &str) -> Vec<Item<'_>> {
    tokenize(line).collect()
}

fn ok<'a>(tokens: &[Token<'a>]) -> Vec<Item<'a>> {
    tokens.iter().copied().map(Ok).collect()
}

/// The tokens that were read before `error`, then the error itself; nothing follows it.
fn then_error<'a>(tokens: &[Token<'a>], error: LexError) -> Vec<Item<'a>> {
    let mut items = ok(tokens);
    items.push(Err(error));
    items
}

#[test]
fn tokens_typical_line() {
    assert_eq!(
        stream("[2024-05-01T12:00:00Z] level=info msg=\"disk 91% full\" retries= done"),
        ok(&[
            Token::Timestamp("2024-05-01T12:00:00Z"),
            Token::Key("level"),
            Token::Bare("info"),
            Token::Key("msg"),
            Token::Quoted("disk 91% full"),
            Token::Key("retries"),
            Token::Bare(""),
            Token::Word("done"),
        ])
    );
}

#[test]
fn tokens_empty_and_blank_lines() {
    assert_eq!(stream(""), vec![]);
    assert_eq!(stream("   "), vec![]);
    assert_eq!(stream(" \t \t"), vec![]);
}

#[test]
fn tokens_leading_and_trailing_blanks_are_ignored() {
    assert_eq!(stream("  \t k=v"), ok(&[Token::Key("k"), Token::Bare("v")]));
    assert_eq!(stream("k=v   "), ok(&[Token::Key("k"), Token::Bare("v")]));
    assert_eq!(stream("k=\"v\"  \t"), ok(&[Token::Key("k"), Token::Quoted("v")]));
    assert_eq!(stream("word \t"), ok(&[Token::Word("word")]));
    assert_eq!(stream("[ts]  "), ok(&[Token::Timestamp("ts")]));
}

#[test]
fn tokens_tabs_and_spaces_both_separate() {
    assert_eq!(
        stream("a=1\tb=2 c"),
        ok(&[Token::Key("a"), Token::Bare("1"), Token::Key("b"), Token::Bare("2"), Token::Word("c")])
    );
    assert_eq!(
        stream("[t]\tk=v"),
        ok(&[Token::Timestamp("t"), Token::Key("k"), Token::Bare("v")])
    );
}

#[test]
fn tokens_timestamp_forms() {
    assert_eq!(stream("[]"), ok(&[Token::Timestamp("")]));
    assert_eq!(stream("[a b c]"), ok(&[Token::Timestamp("a b c")]));
    assert_eq!(stream("[x] [y]"), ok(&[Token::Timestamp("x"), Token::Timestamp("y")]));
    assert_eq!(stream("[x=\"y\"]"), ok(&[Token::Timestamp("x=\"y\"")]));
}

#[test]
fn tokens_timestamp_errors() {
    assert_eq!(stream("[abc"), then_error(&[], LexError::UnterminatedTimestamp { pos: 0 }));
    assert_eq!(
        stream("ok [abc"),
        then_error(&[Token::Word("ok")], LexError::UnterminatedTimestamp { pos: 3 })
    );
    assert_eq!(stream("["), then_error(&[], LexError::UnterminatedTimestamp { pos: 0 }));
    assert_eq!(stream("[a[b]"), then_error(&[], LexError::NestedBracket { pos: 2 }));
    assert_eq!(stream("[[]"), then_error(&[], LexError::NestedBracket { pos: 1 }));
    assert_eq!(stream("[t]k=v"), then_error(&[], LexError::ExpectedSeparator { pos: 3 }));
    assert_eq!(
        stream("a=1 [t]\"x\""),
        then_error(&[Token::Key("a"), Token::Bare("1")], LexError::ExpectedSeparator { pos: 7 })
    );
}

#[test]
fn tokens_pairs_with_bare_values() {
    assert_eq!(stream("k=v"), ok(&[Token::Key("k"), Token::Bare("v")]));
    assert_eq!(stream("k=v=w"), ok(&[Token::Key("k"), Token::Bare("v=w")]));
    assert_eq!(stream("k==v"), ok(&[Token::Key("k"), Token::Bare("=v")]));
    assert_eq!(stream("url=a?b=c&d"), ok(&[Token::Key("url"), Token::Bare("a?b=c&d")]));
    assert_eq!(stream("k=[x]"), ok(&[Token::Key("k"), Token::Bare("[x]")]));
    assert_eq!(
        stream("k=[x y]"),
        ok(&[Token::Key("k"), Token::Bare("[x"), Token::Word("y]")])
    );
}

#[test]
fn tokens_empty_values() {
    assert_eq!(stream("k="), ok(&[Token::Key("k"), Token::Bare("")]));
    assert_eq!(stream("k= z"), ok(&[Token::Key("k"), Token::Bare(""), Token::Word("z")]));
    assert_eq!(
        stream("a=\tb=1"),
        ok(&[Token::Key("a"), Token::Bare(""), Token::Key("b"), Token::Bare("1")])
    );
    assert_eq!(stream("k=\"\""), ok(&[Token::Key("k"), Token::Quoted("")]));
}

#[test]
fn tokens_quoted_values_keep_their_escapes_as_written() {
    assert_eq!(stream(r#"k="a b""#), ok(&[Token::Key("k"), Token::Quoted("a b")]));
    assert_eq!(stream(r#"k="a\"b""#), ok(&[Token::Key("k"), Token::Quoted(r#"a\"b"#)]));
    assert_eq!(stream(r#"k="\\""#), ok(&[Token::Key("k"), Token::Quoted(r"\\")]));
    assert_eq!(stream(r#"k="a\\""#), ok(&[Token::Key("k"), Token::Quoted(r"a\\")]));
    assert_eq!(stream(r#"k="\n\t""#), ok(&[Token::Key("k"), Token::Quoted(r"\n\t")]));
    assert_eq!(
        stream(r#"k="[not a ts] x=y""#),
        ok(&[Token::Key("k"), Token::Quoted("[not a ts] x=y")])
    );
    assert_eq!(stream("k=\"tab\there\""), ok(&[Token::Key("k"), Token::Quoted("tab\there")]));
}

#[test]
fn tokens_quoted_value_must_be_followed_by_a_blank() {
    assert_eq!(
        stream("k=\"a\"\tz"),
        ok(&[Token::Key("k"), Token::Quoted("a"), Token::Word("z")])
    );
    assert_eq!(
        stream("k=\"a\"b"),
        then_error(&[Token::Key("k")], LexError::ExpectedSeparator { pos: 5 })
    );
    assert_eq!(
        stream("k=\"a\"\"b\""),
        then_error(&[Token::Key("k")], LexError::ExpectedSeparator { pos: 5 })
    );
    assert_eq!(
        stream("k=\"a\"=b"),
        then_error(&[Token::Key("k")], LexError::ExpectedSeparator { pos: 5 })
    );
}

#[test]
fn tokens_unterminated_quotes() {
    assert_eq!(
        stream("k=\"abc"),
        then_error(&[Token::Key("k")], LexError::UnterminatedQuote { pos: 2 })
    );
    assert_eq!(
        stream("k=\""),
        then_error(&[Token::Key("k")], LexError::UnterminatedQuote { pos: 2 })
    );
    assert_eq!(
        stream("a=1 msg=\"abc\\"),
        then_error(
            &[Token::Key("a"), Token::Bare("1"), Token::Key("msg")],
            LexError::UnterminatedQuote { pos: 8 }
        )
    );
    assert_eq!(
        stream(r#"k="abc\""#),
        then_error(&[Token::Key("k")], LexError::UnterminatedQuote { pos: 2 })
    );
}

#[test]
fn tokens_invalid_escapes() {
    assert_eq!(
        stream(r#"k="a\qb""#),
        then_error(&[Token::Key("k")], LexError::InvalidEscape { pos: 4 })
    );
    assert_eq!(
        stream(r#"k="\ x""#),
        then_error(&[Token::Key("k")], LexError::InvalidEscape { pos: 3 })
    );
    assert_eq!(
        stream("k=\"\\\u{e9}\""),
        then_error(&[Token::Key("k")], LexError::InvalidEscape { pos: 3 })
    );
    assert_eq!(
        stream(r#"k="\q\"#),
        then_error(&[Token::Key("k")], LexError::InvalidEscape { pos: 3 })
    );
}

#[test]
fn tokens_words() {
    assert_eq!(stream("hello"), ok(&[Token::Word("hello")]));
    assert_eq!(stream("a[0] x] y["), ok(&[Token::Word("a[0]"), Token::Word("x]"), Token::Word("y[")]));
    assert_eq!(stream("a\nb"), ok(&[Token::Word("a\nb")]));
    assert_eq!(stream("k=v\r"), ok(&[Token::Key("k"), Token::Bare("v\r")]));
}

#[test]
fn tokens_quote_where_it_does_not_belong() {
    assert_eq!(stream("\"x\""), then_error(&[], LexError::UnexpectedQuote { pos: 0 }));
    assert_eq!(
        stream("ab\"c"),
        then_error(&[], LexError::UnexpectedQuote { pos: 2 })
    );
    assert_eq!(
        stream("a\"b=c"),
        then_error(&[], LexError::UnexpectedQuote { pos: 1 })
    );
    assert_eq!(
        stream("k=ab\"c"),
        then_error(&[Token::Key("k")], LexError::UnexpectedQuote { pos: 4 })
    );
    assert_eq!(
        stream("k=a\"b\""),
        then_error(&[Token::Key("k")], LexError::UnexpectedQuote { pos: 3 })
    );
}

#[test]
fn tokens_empty_key() {
    assert_eq!(stream("=v"), then_error(&[], LexError::EmptyKey { pos: 0 }));
    assert_eq!(
        stream("a =v"),
        then_error(&[Token::Word("a")], LexError::EmptyKey { pos: 2 })
    );
    assert_eq!(
        stream("[t] =v"),
        then_error(&[Token::Timestamp("t")], LexError::EmptyKey { pos: 4 })
    );
}

#[test]
fn tokens_nothing_follows_an_error() {
    let line = "a=\"x\\q\" b=1 [t]";
    assert_eq!(
        stream(line),
        then_error(&[Token::Key("a")], LexError::InvalidEscape { pos: 4 })
    );
    let mut tokens = tokenize(line);
    assert_eq!(tokens.next(), Some(Ok(Token::Key("a"))));
    assert!(matches!(tokens.next(), Some(Err(_))));
    assert_eq!(tokens.next(), None);
    assert_eq!(tokens.next(), None);
}

#[test]
fn tokens_iterator_stays_finished() {
    for line in ["", "k=", "k=v", "[t]", "word"] {
        let mut tokens = tokenize(line);
        while tokens.next().is_some() {}
        assert_eq!(tokens.next(), None, "{line:?}");
        assert_eq!(tokens.next(), None, "{line:?}");
    }
}

#[test]
fn tokens_non_ascii_text() {
    assert_eq!(
        stream("msg=\"gr\u{fc}\u{df}e \u{2713}\" \u{43a}\u{43b}=\u{437}\u{43d} \u{f1}"),
        ok(&[
            Token::Key("msg"),
            Token::Quoted("gr\u{fc}\u{df}e \u{2713}"),
            Token::Key("\u{43a}\u{43b}"),
            Token::Bare("\u{437}\u{43d}"),
            Token::Word("\u{f1}"),
        ])
    );
    assert_eq!(stream("[\u{2713}]"), ok(&[Token::Timestamp("\u{2713}")]));
}

#[test]
fn tokens_error_positions_are_byte_offsets() {
    assert_eq!(
        stream("\u{e9}\u{e9}=1 =x"),
        then_error(
            &[Token::Key("\u{e9}\u{e9}"), Token::Bare("1")],
            LexError::EmptyKey { pos: 7 }
        )
    );
}

#[test]
fn tokens_borrow_from_the_line() {
    let line = String::from("[ts] key=\"quoted value\" bare=x word");
    let range = line.as_ptr() as usize..line.as_ptr() as usize + line.len();
    let mut count = 0;
    for token in tokenize(&line) {
        let text = match token.unwrap() {
            Token::Timestamp(t) | Token::Key(t) | Token::Quoted(t) | Token::Bare(t) | Token::Word(t) => t,
        };
        let start = text.as_ptr() as usize;
        assert!(range.contains(&start) && start + text.len() <= range.end, "{text:?} is a copy");
        count += 1;
    }
    assert_eq!(count, 6);
}

#[test]
fn tokens_long_line_keeps_every_pair() {
    let line: String = (0..500).map(|i| format!("k{i}=v{i} ")).collect();
    let tokens = stream(&line);
    assert_eq!(tokens.len(), 1000);
    assert_eq!(tokens[0], Ok(Token::Key("k0")));
    assert_eq!(tokens[999], Ok(Token::Bare("v499")));
}
