<p align="center">
  <img src="docs/assets/banner.svg" alt="clean-code: Clean Code nach Robert C. Martin, für Coding-Agents" width="100%">
</p>

<p align="center"><a href="README.md">English</a> · Deutsch</p>

Ein [Agent Skill](https://agentskills.io), der Coding-Agents *Clean Code* nach Robert C. Martin beibringt, inklusive Becks vier Regeln des einfachen Designs und des vollständigen Smell-Katalogs C1–T9. Er passt das Buch an die Fehler an, die Agents tatsächlich machen.

Die meisten Clean-Code-Skills geben das Buch wieder. Dieser sagt dem Agent zusätzlich, **wann das Buch verliert**: wenn die Sprache ein anderes Idiom hat, wenn die Codebasis eine Konvention hat, wenn der Code ein Hot Path ist, oder wenn „Aufräumen“ bedeutet, Code anzufassen, nach dem niemand gefragt hat.

Der Skill selbst ist auf Englisch, damit er in jedem Agent und für jedes Team funktioniert. Der Agent antwortet trotzdem in deiner Sprache.

## Was er anders macht

<p align="center">
  <img src="docs/assets/precedence.svg" alt="Vorrang: 1 korrekt und geprüft, 2 Codebasis und Sprache, 3 Becks vier Regeln, 4 Heuristiken C1–T9" width="760">
</p>

1. **Eine Vorrangregel.** Korrektheit zuerst, dann Projektkonventionen und Sprachidiome, dann Becks Regeln, dann die Heuristiken. Jede gebogene Regel braucht eine einzeilige Begründung.
2. **Scope-Disziplin und typische Agent-Fehler.** Vor dem Schreiben suchen, Diff auf die Aufgabe begrenzen, keine spekulativen Abstraktionen, keine verschluckten Fehler, keine Kommentare, die die Änderung nacherzählen, kein ungeprüftes „Tests grün“.
3. **Ausdrückliche Ausnahmen.** Hot Paths, generierter Code, Wegwerf-Skripte, Konsistenz mit Legacy-Code, tiefe Module.

## Ergebnisse

Acht realistische Coding-Aufgaben in Python, TypeScript, Java, Go, Kotlin, C# und JavaScript, je dreimal unter vier Bedingungen: ohne Skill, mit sickn33/clean-code (dem Clean-Code-Skill mit den meisten Installationen auf skills.sh, Stand November 2026), mit der ersten Version dieses Skills und mit der aktuellen. Claude Sonnet 5.5 schreibt den Code, Claude Opus 5.5 bewertet unter vertauschten Bezeichnungen.

<p align="center">
  <img src="docs/assets/results-quality.svg" alt="Qualitätsurteil: ohne Skill 7,5, sickn33 7,5, v1 6,2, v2 8,4" width="49%">
  <img src="docs/assets/results-pass-rate.svg" alt="Erfüllte Kriterien: ohne Skill 95,8 %, sickn33 92,5 %, v1 89,2 %, v2 99,2 %" width="49%">
</p>

- **Ein starkes Modell kann das schon gut.** Ohne Skill erfüllt Sonnet 95,8 % der Kriterien. Ein Clean-Code-Skill kann wenig gewinnen und einiges verschlechtern.
- **Ein Skill kann schaden.** sickn33/clean-code fällt beim Hot Path auf 60 %: Bit-Tests wandern in Hilfsmethoden innerhalb der Paket-Schleife, und die vage Exception bleibt. Die erste Version dieses Skills fällt bei Kotlin auf 60 %, weil sie `String?` durch eine Exception ersetzt.
- **v2 erfüllt in jeder Aufgabe mindestens so viele Kriterien wie ohne Skill** und hebt das durchschnittliche Qualitätsurteil von 7,5 auf 8,4. Beim PR-Review liegt das Qualitätsurteil knapp darunter (8,0 statt 8,3).

Das ist eine Plausibilitätsprüfung, keine Rangliste: acht Fälle, ein KI-Bewerter, der skill-gestützte Antworten teilweise erkennen kann (sie zitieren Heuristik-Codes), und Fälle, die zusammen mit v2 entstanden sind. Methode, Grenzen und alle Rohdaten: [`evals/README.md`](evals/README.md).

## Installation

```bash
npx skills add jonax1337/clean-code-skill
```

In Claude Code alternativ als Plugin:

```text
/plugin marketplace add jonax1337/clean-code-skill
/plugin install clean-code@clean-code-skill
```

Oder manuell `skills/clean-code` nach `~/.claude/skills/` kopieren.

## Nutzung

Der Skill greift automatisch, sobald der Agent Code schreibt, ändert, refaktoriert oder reviewt. Direkt aufrufen geht mit `/clean-code <pfad>`, als Claude-Code-Plugin mit `/clean-code:clean-code <pfad>`. Soll er immer gelten, genügt eine Zeile in `CLAUDE.md` oder `AGENTS.md`:

```markdown
Before writing, changing or reviewing code, load the clean-code skill and follow it.
```

## Hinweis

Basiert auf *Clean Code* von Robert C. Martin (2008) und Kent Becks Regeln des einfachen Designs. Das Projekt ist weder mit den Autoren verbunden noch von ihnen autorisiert. Der Skill gibt die Ideen sinngemäß wieder; die Begründungen stehen im Buch.

Lizenz: [MIT](LICENSE)
