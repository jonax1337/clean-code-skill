pub mod cli;
mod error;
mod parse;
mod render;

pub use error::CliError;

/// Runs the tool on already-read input and returns what should be printed.
pub fn run(args: &[&str], input: &str) -> Result<String, CliError> {
    match cli::parse_args(args)? {
        cli::Command::Help => Ok(cli::USAGE.to_string()),
        cli::Command::Render(options) => {
            let rows = parse::split_rows(input, options.delimiter);
            Ok(render::render_table(&rows, &options))
        }
    }
}
