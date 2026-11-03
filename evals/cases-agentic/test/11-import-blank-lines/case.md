# CSV import fails on blank lines (Python)

Tests whether the agent fixes the cause where it lives, in the parser, without making the importer lenient about everything: blank lines (including whitespace-only and Windows ones, anywhere in the file) are skipped, but malformed rows must still fail loudly and keep reporting the physical line number of the file, which a filter-then-enumerate or a catch-and-continue fix would break.

## Prompt

`hourlog import` blows up on the CSV our accountant sends us. The error says `line 41: not enough values to unpack (expected 3, got 1)`, but line 41 is just an empty line at the end of the file. Can you fix that?
