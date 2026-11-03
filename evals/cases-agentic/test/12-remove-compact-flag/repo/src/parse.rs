/// Splits delimited text into rows of cells. Blank lines are skipped.
pub fn split_rows(input: &str, delimiter: char) -> Vec<Vec<String>> {
    input
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| line.split(delimiter).map(str::to_string).collect())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_on_the_delimiter() {
        assert_eq!(
            split_rows("a,b\nc,d\n", ','),
            vec![vec!["a", "b"], vec!["c", "d"]]
        );
    }

    #[test]
    fn skips_blank_lines() {
        assert_eq!(split_rows("a\n\n  \nb\n", ','), vec![vec!["a"], vec!["b"]]);
    }

    #[test]
    fn keeps_empty_cells() {
        assert_eq!(split_rows("a,,c\n", ','), vec![vec!["a", "", "c"]]);
    }
}
