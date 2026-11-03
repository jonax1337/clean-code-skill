//! The public API is unchanged: names, signatures, variants and trait implementations are fixed by compiling this.

use std::borrow::Cow;
use std::fmt::{Debug, Display};

use logscan::{tokenize, unescape, LexError, Stats, Token, Tokens};

fn is_copy_and_comparable<T: Copy + Clone + Debug + PartialEq + Eq>() {}

fn is_error<T: std::error::Error + Display>() {}

fn is_token_stream<'a, I: Iterator<Item = Result<Token<'a>, LexError>> + Clone + Debug>() {}

fn text<'a>(token: Token<'a>) -> &'a str {
    match token {
        Token::Timestamp(text)
        | Token::Key(text)
        | Token::Quoted(text)
        | Token::Bare(text)
        | Token::Word(text) => text,
    }
}

fn position(error: LexError) -> usize {
    match error {
        LexError::UnterminatedTimestamp { pos }
        | LexError::NestedBracket { pos }
        | LexError::UnterminatedQuote { pos }
        | LexError::InvalidEscape { pos }
        | LexError::UnexpectedQuote { pos }
        | LexError::EmptyKey { pos }
        | LexError::ExpectedSeparator { pos } => pos,
    }
}

#[test]
fn api_functions_keep_their_signatures() {
    let _: for<'a> fn(&'a str) -> Tokens<'a> = tokenize;
    let _: for<'a> fn(&'a str) -> Cow<'a, str> = unescape;
    let _: fn(&mut Stats, &str) = Stats::add_line;
}

#[test]
fn api_types_keep_their_traits() {
    is_copy_and_comparable::<Token<'static>>();
    is_copy_and_comparable::<LexError>();
    is_error::<LexError>();
    is_token_stream::<Tokens<'static>>();
}

#[test]
fn api_variants_and_payloads_are_unchanged() {
    assert_eq!(text(Token::Quoted("q")), "q");
    assert_eq!(position(LexError::EmptyKey { pos: 9 }), 9);
}

#[test]
fn api_tokens_outlive_the_iterator() {
    let line = String::from("a=1");
    let first = {
        let mut tokens = tokenize(&line);
        tokens.next()
    };
    assert_eq!(first, Some(Ok(Token::Key("a"))));
}

#[test]
fn api_tokens_can_be_built_directly() {
    assert_eq!(Tokens::new("a").next(), tokenize("a").next());
}

#[test]
fn api_cloned_iterator_continues_independently() {
    let mut original = tokenize("a=1 b=2");
    original.next();
    let rest: Vec<_> = original.clone().collect();
    assert_eq!(rest.len(), 3);
    assert_eq!(original.collect::<Vec<_>>(), rest);
}

#[test]
fn api_errors_are_described() {
    assert_eq!(
        LexError::InvalidEscape { pos: 4 }.to_string(),
        "unknown escape sequence at 4"
    );
}

#[test]
fn api_stats_counts_stay_the_same() {
    let mut stats = Stats::default();
    stats.add_line("[t] a=1 b=\"x\" w");
    stats.add_line("c=\"open");
    stats.add_line("");
    assert_eq!(
        stats,
        Stats { lines: 3, rejected_lines: 1, timestamps: 1, pairs: 3, words: 1 }
    );
}

#[test]
fn api_unescape_still_resolves_escapes() {
    assert_eq!(unescape(r#"a\"b\n"#), "a\"b\n");
    assert!(matches!(unescape("plain"), Cow::Borrowed("plain")));
}
