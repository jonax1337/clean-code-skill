use std::borrow::Cow;

/// Resolves the escapes of a quoted value as the tokenizer hands it out. Borrows when there is nothing to resolve.
pub fn unescape(raw: &str) -> Cow<'_, str> {
    if !raw.contains('\\') {
        return Cow::Borrowed(raw);
    }
    let mut text = String::with_capacity(raw.len());
    let mut chars = raw.chars();
    while let Some(c) = chars.next() {
        if c != '\\' {
            text.push(c);
            continue;
        }
        match chars.next() {
            Some('n') => text.push('\n'),
            Some('t') => text.push('\t'),
            Some(other) => text.push(other),
            None => text.push('\\'),
        }
    }
    Cow::Owned(text)
}
