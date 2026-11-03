# Making configuration errors visible (Java)

Tests whether the agent turns a loader that silently falls back to defaults into one that fails loudly, without overshooting. `ConfigLoader` swallows errors in several shapes: an `IOException` on the file that is ignored, a `catch (Exception)` that returns `null` for the upstream URL, a `NumberFormatException` and a range check that both fall back to the default, a timeout parser that falls back when the format is wrong, and `Boolean.parseBoolean`, which turns the typo `ture` into `false` without any catch block at all. Two keys are required and five are optional with documented defaults. A missing optional key must keep using its default; only a present but malformed value is an error. The error must name the key and the bad value, keep the cause, come from the loader without `System.exit`, and the entry point must turn it into a short startup failure (no stack trace, nothing processed). Two existing tests pin the old fallback behavior and have to be rewritten.

## Prompt

Last week ops lost a few hours because someone typo'd a value in config.properties (a worker count with a letter in it). The relay quietly ran on its defaults and nobody noticed until throughput tanked. Can you make sure that can't happen again? If the configuration is wrong, the relay should refuse to start and tell whoever is deploying it what is wrong.
