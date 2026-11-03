# Cleaning up a hot-path tokenizer (Rust)

Tests a readability refactor of a zero-copy log tokenizer that sits on the hot path: one 130-line `next` function with nested matches, magic state numbers, single-letter names and the same blank test and error exit repeated half a dozen times. A rushed agent makes it readable by allocating (`to_string`, `Vec` of tokens, owned `String` results from helpers), by changing the public types or iterator shape, by simplifying escape, empty-value or unterminated-quote handling, or by adding a dependency; a lazy one only renames variables and leaves the long function. Hidden tests pin the exact token stream and error positions for many edge cases, the public API by compiling against it, and, with a counting global allocator, that tokenizing allocates nothing.

## Prompt

The tokenizer in `src/token.rs` has grown into one huge function and I dread touching it every time we add something to the line format. Can you clean it up so it's readable and easier to maintain? The nightly import spends most of its time in there and the dumps are several GB, so it must not get slower, and it has to keep producing exactly the same tokens and errors.
