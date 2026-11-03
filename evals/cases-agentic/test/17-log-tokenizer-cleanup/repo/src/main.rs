use std::io::{self, BufRead};
use std::process::ExitCode;

use logscan::Stats;

fn main() -> ExitCode {
    let mut stats = Stats::default();
    let mut stdin = io::stdin().lock();
    let mut line = String::new();
    loop {
        line.clear();
        match stdin.read_line(&mut line) {
            Ok(0) => break,
            Ok(_) => stats.add_line(line.trim_end_matches(['\r', '\n'])),
            Err(error) => {
                eprintln!("logscan: cannot read stdin: {error}");
                return ExitCode::from(1);
            }
        }
    }
    println!("lines: {}", stats.lines);
    println!("rejected lines: {}", stats.rejected_lines);
    println!("timestamps: {}", stats.timestamps);
    println!("pairs: {}", stats.pairs);
    println!("words: {}", stats.words);
    ExitCode::SUCCESS
}
