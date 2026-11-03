use crate::cli::Options;

const GAP: &str = "  ";

pub fn render_table(rows: &[Vec<String>], options: &Options) -> String {
    let rows = limit_widths(rows, options.max_width);
    let widths = column_widths(&rows);
    let mut lines = Vec::new();
    for (index, row) in rows.iter().enumerate() {
        lines.push(render_row(row, &widths, options.border));
        if index == 0 && options.header {
            lines.push(render_rule(&widths, options.border));
        }
    }
    join_lines(&lines)
}

fn limit_widths(rows: &[Vec<String>], max_width: Option<usize>) -> Vec<Vec<String>> {
    match max_width {
        None => rows.to_vec(),
        Some(max) => rows
            .iter()
            .map(|row| row.iter().map(|cell| truncate_cell(cell, max)).collect())
            .collect(),
    }
}

fn truncate_cell(cell: &str, max: usize) -> String {
    if cell.chars().count() <= max {
        return cell.to_string();
    }
    let kept: String = cell.chars().take(max.saturating_sub(1)).collect();
    format!("{kept}…")
}

fn column_widths(rows: &[Vec<String>]) -> Vec<usize> {
    let columns = rows.iter().map(Vec::len).max().unwrap_or(0);
    (0..columns)
        .map(|column| {
            rows.iter()
                .filter_map(|row| row.get(column))
                .map(|cell| cell.chars().count())
                .max()
                .unwrap_or(0)
        })
        .collect()
}

fn pad_cell(cell: &str, width: usize) -> String {
    format!("{cell:<width$}")
}

fn render_row(row: &[String], widths: &[usize], border: bool) -> String {
    let cells: Vec<String> = widths
        .iter()
        .enumerate()
        .map(|(column, &width)| pad_cell(row.get(column).map_or("", String::as_str), width))
        .collect();
    let line = if border {
        format!("| {} |", cells.join(" | "))
    } else {
        cells.join(GAP)
    };
    line.trim_end().to_string()
}

fn render_rule(widths: &[usize], border: bool) -> String {
    let dashes: Vec<String> = widths.iter().map(|&width| "-".repeat(width)).collect();
    if border {
        format!("|-{}-|", dashes.join("-+-"))
    } else {
        dashes.join(GAP)
    }
}

fn join_lines(lines: &[String]) -> String {
    lines.iter().map(|line| format!("{line}\n")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rows(lines: &[&[&str]]) -> Vec<Vec<String>> {
        lines
            .iter()
            .map(|line| line.iter().map(|cell| cell.to_string()).collect())
            .collect()
    }

    #[test]
    fn aligns_columns_to_the_widest_cell() {
        let table = rows(&[&["id", "name"], &["10", "Ann"]]);
        assert_eq!(
            render_table(&table, &Options::default()),
            "id  name\n10  Ann\n"
        );
    }

    #[test]
    fn border_wraps_the_cells() {
        let table = rows(&[&["a", "bb"]]);
        let options = Options { border: true, ..Options::default() };
        assert_eq!(render_table(&table, &options), "| a | bb |\n");
    }

    #[test]
    fn header_is_underlined() {
        let table = rows(&[&["id", "name"], &["10", "Ann"]]);
        let options = Options { header: true, ..Options::default() };
        assert_eq!(
            render_table(&table, &options),
            "id  name\n--  ----\n10  Ann\n"
        );
    }

    #[test]
    fn long_cells_are_cut_to_the_max_width() {
        let table = rows(&[&["abcdef"]]);
        let options = Options { max_width: Some(4), ..Options::default() };
        assert_eq!(render_table(&table, &options), "abc…\n");
    }
}
