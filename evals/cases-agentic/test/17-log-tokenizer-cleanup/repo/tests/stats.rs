use logscan::{unescape, Stats};

#[test]
fn counts_tokens_by_kind() {
    let mut stats = Stats::default();
    stats.add_line("[2024-05-01T12:00:00Z] level=info msg=\"a b\" started");
    stats.add_line("[2024-05-01T12:00:01Z] level=warn");
    assert_eq!(
        stats,
        Stats { lines: 2, rejected_lines: 0, timestamps: 2, pairs: 3, words: 1 }
    );
}

#[test]
fn rejected_lines_are_counted_once() {
    let mut stats = Stats::default();
    stats.add_line("a=\"open");
    stats.add_line("fine=1");
    assert_eq!(stats.lines, 2);
    assert_eq!(stats.rejected_lines, 1);
    assert_eq!(stats.pairs, 2);
}

#[test]
fn unescape_resolves_the_known_escapes() {
    assert_eq!(unescape(r#"a \"b\"\tc\\"#), "a \"b\"\tc\\");
    assert_eq!(unescape("plain"), "plain");
}
