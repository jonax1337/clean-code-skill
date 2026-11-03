//! Tokenizing must not allocate: a counting allocator watches every token of a large mixed input, errors included.

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;
use std::hint::black_box;

use logscan::{tokenize, Token};

thread_local! {
    static ALLOCATIONS: Cell<usize> = const { Cell::new(0) };
}

struct CountingAllocator;

fn count_allocation() {
    ALLOCATIONS.with(|count| count.set(count.get() + 1));
}

unsafe impl GlobalAlloc for CountingAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        count_allocation();
        System.alloc(layout)
    }

    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
        count_allocation();
        System.alloc_zeroed(layout)
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        count_allocation();
        System.realloc(ptr, layout, new_size)
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout)
    }
}

#[global_allocator]
static ALLOCATOR: CountingAllocator = CountingAllocator;

fn corpus() -> Vec<String> {
    let mut lines = Vec::new();
    for i in 0..2_000 {
        lines.push(format!(
            "[2024-05-01T12:{:02}:{:02}Z] level=info msg=\"request \\\"{i}\\\" took 12ms\" user=u{i} retries= done",
            i / 60 % 60,
            i % 60
        ));
        lines.push(format!("k{i}=v{i}\tflag  other=\"a b\"  tail"));
    }
    for broken in [
        "msg=\"never closed",
        "msg=\"bad \\q escape\"",
        "[no end",
        "[a[b]",
        "=value",
        "ab\"c",
        "k=\"a\"b",
        "k=a\"b",
        "[t]x",
        "msg=\"ends with backslash\\",
    ] {
        for _ in 0..200 {
            lines.push(broken.to_string());
        }
    }
    lines
}

#[test]
fn alloc_tokenizing_never_allocates() {
    let lines = corpus();
    let before = ALLOCATIONS.with(Cell::get);
    let mut tokens = 0usize;
    let mut errors = 0usize;
    for line in &lines {
        for token in tokenize(black_box(line)) {
            match token {
                Ok(Token::Timestamp(_) | Token::Key(_) | Token::Quoted(_) | Token::Bare(_) | Token::Word(_)) => {
                    tokens += 1;
                }
                Err(_) => errors += 1,
            }
        }
    }
    let allocations = ALLOCATIONS.with(Cell::get) - before;
    assert!(tokens > 0 && errors > 0, "the corpus was not tokenized: {tokens} tokens, {errors} errors");
    assert_eq!(allocations, 0, "tokenizing {tokens} tokens allocated {allocations} times");
}
