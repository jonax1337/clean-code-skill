# Judge agreement: opus and gpt-6.1-sol

Coder sonnet, test cases. A score is the share of verdicts the first condition of the pair
won (ties count half). Same side: both judges prefer the same condition, or both call it even. The pooled
kappa mixes pairs with different base rates; read the per-pair rows first.

| Pair | Comparisons | First wins, default judge | First wins, other judge | Same side | Kappa |
|---|---|---|---|---|---|
| none vs this-repo | 26 | 0.06 | 0.19 | 77% | 0.07 |
| this-repo vs claudemd-baseline | 13 | 0.73 | 0.77 | 77% | 0.44 |
| all pairs, pooled | 39 | 0.28 | 0.38 | 77% | 0.51 |

| Dimension | Same side | Kappa |
|---|---|---|
| correctness | 85% | 0.67 |
| scope | 87% | 0.59 |
| design | 72% | 0.46 |
| readability | 56% | 0.34 |
| tests | 87% | 0.71 |
| report | 49% | 0.24 |
