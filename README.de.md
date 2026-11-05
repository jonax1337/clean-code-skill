<p align="center">
  <img src="docs/assets/banner.png" alt="Clean Code Skill — The right change. Right here." width="100%">
</p>

<p align="center"><a href="README.md">English</a> · Deutsch</p>

**Clean Code Skill** ist ein [Agent Skill](https://agentskills.io), der Coding-Agents *Clean Code* nach Robert C. Martin beibringt, inklusive Becks vier Regeln des einfachen Designs und des vollständigen Smell-Katalogs C1–T9. Er passt das Buch an die Fehler an, die Agents tatsächlich machen.

Die meisten Clean-Code-Skills geben das Buch wieder. Dieser sagt dem Agent zusätzlich, **wann das Buch verliert**: wenn die Sprache ein anderes Idiom hat, wenn die Codebasis eine Konvention hat, wenn der Code ein Hot Path ist, oder wenn „Aufräumen“ bedeutet, Code anzufassen, nach dem niemand gefragt hat.

Der Skill selbst ist auf Englisch, damit er in jedem Agent und für jedes Team funktioniert. Der Agent antwortet trotzdem in deiner Sprache.

<p align="center">
  <img src="docs/assets/highlights.svg" alt="Ergebnisse auf einen Blick, 13 zurückgehaltene Aufgaben, blinder paarweiser Bewerter: gegenüber ohne Skill in 94 % der Urteile bevorzugt mit Claude Sonnet 5.5 und in 71 % mit Claude Opus 5.5; lädt sich auf 11 von 13 Aufgaben selbst, die anderen Clean-Code-Skills in 2 von 46 Läufen; vier Sätze in CLAUDE.md holen einen Teil des Vorsprungs" width="880">
</p>

## Was er anders macht

<p align="center">
  <img src="docs/assets/precedence.svg" alt="Vorrang: 1 korrekt und geprüft, 2 Codebasis und Sprache, 3 Becks vier Regeln, 4 Heuristiken C1–T9" width="760">
</p>

1. **Eine Vorrangregel.** Korrektheit zuerst, dann Projektkonventionen und Sprachidiome, dann Becks Regeln, dann die Heuristiken. Jede gebogene Regel braucht eine einzeilige Begründung.
2. **Scope-Disziplin und typische Agent-Fehler.** Vor dem Schreiben suchen, Diff auf die Aufgabe begrenzen, keine spekulativen Abstraktionen oder Parameter, keine verschluckten Fehler, keine Kommentare, die die Änderung nacherzählen, kein ungeprüftes „Tests grün“. Ist die Aufgabe ein Aufräumen, gehört die ganze Einheit dazu.
3. **Ausdrückliche Ausnahmen.** Hot Paths, generierter Code, Wegwerf-Skripte, Konsistenz mit Legacy-Code, tiefe Module.
4. **Geprüfte Arbeit, ehrlich berichtet.** Ungetesteten Code vor dem Refactoring mit Charakterisierungstests festhalten, jeden Fix und jedes sichtbare Verhalten mit einem Test absichern, Typechecker und Tests entscheiden lassen, was sicher ist, das Design gegen die Zahlen der Aufgabe prüfen und am Ende nur berichten, was geprüft wurde.
5. **Eine Beschreibung, die ihn laden lässt.** Sie sagt dem Agent, den Skill vor dem ersten Edit jeder Coding-Aufgabe zu laden, damit er benutzt wird, ohne dass jemand danach fragt.

## Ergebnisse

Zwei Benchmarks vergleichen den Skill, wie er im Repository steht, mit „ohne Skill“ und mit vier anderen Clean-Code-Skills: [unclebob/ub-mode](https://github.com/unclebob/ub-mode) von Robert C. Martin, [sickn33/clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) (der Clean-Code-Skill mit den meisten Installationen auf skills.sh, Stand November 2026), [ertugrul-dmr/clean-code-skills](https://github.com/ertugrul-dmr/clean-code-skills) (nur Python und TypeScript) und [btseee/clean-code-skills](https://github.com/btseee/clean-code-skills). Der agentische Benchmark hat außerdem eine billige Baseline ganz ohne Skill: vier Sätze in `CLAUDE.md`, die genau die Gewohnheiten verlangen, aus denen der Vorsprung des Skills kommt (Diff im Scope, Tests, Testlauf am Ende, ehrlicher Bericht). Der agentische Benchmark ist der wichtigere: Der Agent arbeitet mit echten Werkzeugen in einem echten Repository, und 13 der 20 Aufgaben blieben bei der Weiterentwicklung des Skills unter Verschluss.

### Agentischer Benchmark: echte Repositories, zurückgehaltene Aufgaben

Der Agent bekommt eine frische Kopie eines kleinen Repositories in Python, TypeScript, JavaScript, Java oder Rust und die üblichen Werkzeuge von Claude Code: lesen, suchen, editieren, Shell. Deterministische Checks bewerten, was er getan hat: versteckte Tests, geänderte Dateien, ob sein Regressionstest auf dem alten Code fehlschlägt, ob seine Tests eingebaute Fehler finden, ob er nach dem letzten Edit die Tests ausgeführt hat. Danach liest ein blinder Bewerter (Claude Opus 5.5) zwei Pull Requests zur selben Aufgabe, in beiden Reihenfolgen, und sagt, welchen er lieber mergen würde und welcher bei Korrektheit, Scope, Design, Lesbarkeit, Tests und Bericht besser ist. Jede der 13 zurückgehaltenen Aufgaben lief zweimal pro Modell und Bedingung (die später hinzugekommene `CLAUDE.md`-Baseline und btseee einmal). Für diese Ergänzungen war der Skill auf Commit `c10f424` eingefroren.

<p align="center">
  <img src="docs/assets/agentic-preference.svg" alt="Blinder Bewerter auf 13 zurückgehaltenen Aufgaben, dieser Skill gegen jede Alternative. Sonnet: 24 von 26 gegen ohne Skill (94 %), 9 von 13 gegen die CLAUDE.md-Baseline (73 %, Intervall reicht bis 50 %), 26 von 26 gegen ub-mode (100 %), 20 gegen sickn33 (84 %), 9 von 14 gegen ertugrul-dmr (79 %), 11 von 13 gegen btseee (90 %). Opus: 18 gegen ohne Skill (71 %), 6 von 13 gegen die CLAUDE.md-Baseline (54 %, Intervall schließt 50 % ein), 19 gegen ub-mode (81 %), 18 gegen sickn33 (74 %), 7 von 14 gegen ertugrul-dmr (59 %, Intervall schließt 50 % ein), 6 von 13 gegen btseee (60 %, Intervall schließt 50 % ein)" width="760">
</p>

| Coding-Agent | gegen ohne Skill | gegen `CLAUDE.md`-Baseline (1 Lauf) | gegen ub-mode | gegen sickn33 | gegen ertugrul-dmr (7 Aufgaben) | gegen btseee (1 Lauf) | Kosten pro Lauf: ohne Skill → Baseline → dieser Skill |
|---|---|---|---|---|---|---|---|
| Claude Sonnet 5.5 | 24 / 1 / 1 · 94 % | 9 / 1 / 3 · 73 %\* | 26 / 0 / 0 · 100 % | 20 / 5 / 1 · 84 % | 9 / 4 / 1 · 79 % | 11 / 2 / 0 · 90 % | 0,09 $ → 0,11 $ → 0,17 $ |
| Claude Opus 5.5 | 18 / 1 / 7 · 71 % | 6 / 2 / 5 · 54 %\* | 19 / 4 / 3 · 81 % | 18 / 3 / 5 · 74 % | 7 / 3 / 4 · 59 %\* | 6 / 3 / 4 · 60 %\* | 0,24 $ → 0,26 $ → 0,33 $ |

Siege / Unentschieden / Niederlagen dieses Skills und die Präferenz des Bewerters für ihn, ein Unentschieden zählt halb. \* Das 95-%-Intervall schließt 50 % ein; das ist ein Trend, kein Ergebnis. Baseline und btseee liefen einmal pro Aufgabe; ihre Intervalle ziehen die Aufgaben neu und sind etwa doppelt so breit (Sonnet gegen die Baseline: 50–92 %).

- **Vier Sätze in `CLAUDE.md` holen einen großen Teil des Vorsprungs.** Gegen ohne Skill gewann die Baseline allein mit Sonnet 9 von 13 Vergleichen (69 %), fast nur über die Tests. Dieser Skill schlägt die Baseline mit Sonnet trotzdem in 9 von 13 Aufgaben; mit Opus liegen beide gleichauf (54 %). Der große Vorsprung gegen ohne Skill heißt also „Gewohnheiten plus Clean-Code-Regeln“, nicht Clean-Code-Regeln allein.
- **Was der Skill über die Baseline hinaus bringt, hängt vom Modell ab.** Anteil der Urteile pro Dimension, die an diesen Skill gingen:

  | Dimension | Sonnet gegen ohne Skill | Sonnet gegen Baseline | Opus gegen ohne Skill | Opus gegen Baseline | Baseline gegen ohne Skill (Sonnet) |
  |---|---|---|---|---|---|
  | Tests | 93 % | 54 % | 70 % | 48 % | 88 % |
  | Bericht | 78 % | 60 % | 76 % | 71 % | 58 % |
  | Lesbarkeit | 78 % | 75 % | 42 % | 48 % | 62 % |
  | Design | 62 % | 62 % | 52 % | 44 % | 56 % |
  | Korrektheit | 57 % | 63 % | 53 % | 44 % | 38 % |
  | Scope | 49 % | 54 % | 54 % | 52 % | 50 % |

  Die Baseline kauft die Tests. Mit Sonnet bleibt dem Skill gegen die Baseline ein Vorsprung bei Lesbarkeit, Design und Korrektheit, der Clean-Code-Teil zeigt sich also im Code. Mit Opus bleibt nur der Bericht; Korrektheit und Design liegen gleichauf oder knapp hinter der Baseline.
- **Ein Bewerter aus einer anderen Modellfamilie sieht dieselbe Richtung.** GPT 6.1 Sol hat jeden Sonnet-Vergleich gegen ohne Skill und gegen die Baseline noch einmal blind und in beiden Reihenfolgen bewertet. Er bevorzugte diesen Skill in 21 von 26 Vergleichen gegen ohne Skill (81 %, Opus: 94 %) und in 10 von 13 gegen die Baseline (77 %, Opus: 73 %). Die beiden Bewerter wählten in 77 % der 39 Vergleiche dieselbe Seite und sind sich bei Tests, Korrektheit und Scope weitgehend einig, bei Lesbarkeit und Bericht nicht (56 % und 49 % dieselbe Seite). Der Lesbarkeitsvorsprung des Skills ist vor allem die Sicht von Opus; die Berichte hält GPT für etwa gleich gut. Details: [`evals/results/agentic/judge-agreement.md`](evals/results/agentic/judge-agreement.md).
- **Die Checks trennen auf den zurückgehaltenen Aufgaben kaum.** Dort bestehen alle Bedingungen 94–99 %, also entscheidet der Bewerter. Auf den Dev-Aufgaben, an denen der Skill verbessert wurde, trennen sie noch: ohne Skill 82 %, die Baseline 93 %, dieser Skill 100 %.
- **Der Skill kostet mehr.** Ein Lauf ist 35–82 % teurer als ohne Skill und braucht mehr Schritte (Sonnet: 12,8 statt 9,3), vor allem fürs Schreiben und Ausführen von Tests. Die Baseline kostet 5–20 % mehr als ohne Skill.

<p align="center">
  <img src="docs/assets/agentic-checks.svg" alt="Erfüllte Checks mit Sonnet. Dev-Aufgaben: ohne Skill 82 %, dieser Skill 100 %, ub-mode 95 %, sickn33 88 %, ertugrul-dmr 89 %, btseee 96 %, CLAUDE.md-Baseline 93 % (die letzten beiden mit einem Lauf pro Aufgabe). Zurückgehaltene Aufgaben: ohne Skill 96 %, dieser Skill 98 %, ub-mode 97 %, sickn33 99 %, ertugrul-dmr 98 %, btseee 96 %, CLAUDE.md-Baseline 99 %" width="760">
</p>

#### Lädt sich ein Skill von selbst?

Oben steht der Skill im System-Prompt. Im echten Einsatz liegt er neben dem Code, und der Agent entscheidet, ob er ihn lädt. Claude Sonnet 5.5, zurückgehaltene Aufgaben, je ein Lauf:

| Als Projekt-Skill installiert … | Dieser Skill | ub-mode | sickn33 | ertugrul-dmr | btseee |
|---|---|---|---|---|---|
| und nirgends erwähnt | **11 / 13** | 0 / 13 | 0 / 13 | 1 / 7 | 1 / 13 |
| mit einer Zeile in `CLAUDE.md` ([unten](#nutzung)) | 13 / 13 | 13 / 13 | 13 / 13 | 7 / 7 | 13 / 13 |

Dieser Skill hat sich bei jeder Aufgabe selbst geladen außer beim PR-Review, bei dem nichts editiert wird, und bei einer Performance-Aufgabe. ub-mode ist dafür gedacht, mit `/ub-mode` eingeschaltet zu werden, und soll sich gar nicht selbst laden; btseee soll sich laut seinem README selbst laden, tat das aber nur bei einer Aufgabe, dem Tokenizer-Aufräumen. Mit der einen Zeile in `CLAUDE.md` lud sich jeder Skill in jedem Lauf. Bei fünf Aufgaben ohne Code (Gedicht, E-Mail, Frage zu TCP, README zusammenfassen, Regex erklären) lud sich dieser Skill nie.

13 Aufgaben mit zwei Läufen pro Zelle (einem für Baseline und btseee) sind wenig, und die Intervalle beschreiben diese Aufgaben, nicht Aufgaben im Allgemeinen. Nur Claude-Modelle haben den Code geschrieben. Der Hauptbewerter ist Claude Opus, das auch die Hälfte des hier berichteten Codes geschrieben hat; er weiß nicht, welcher Skill welchen Pull Request geschrieben hat, könnte aber Code bevorzugen, der wie sein eigener aussieht, deshalb hat GPT 6.1 Sol die Sonnet-Vergleiche noch einmal bewertet. ub-mode wurde ohne seine Begleit-Tools gemessen, btseee ohne sein einmaliges `init` (siehe [`evals/README.md`](evals/README.md#conditions)). Nach den finalen Läufen stellte sich heraus, dass ein Check Commit-Nachrichten als Dateizugriffe las; das traf nur ub-mode, den einzigen Skill, der den Agent committen lässt. Der Check wurde korrigiert und jeder Lauf neu bewertet. Alle Grenzen stehen in [`evals/README.md`](evals/README.md#limits).

### Single-Turn-Suite

Acht realistische Coding-Aufgaben in Python, TypeScript, Java, Go, Kotlin, C# und JavaScript, je eine Antwort ohne Werkzeuge, je dreimal pro Bedingung. Claude Sonnet 5.5 schreibt den Code, Claude Opus 5.5 bewertet alle Antworten einer Aufgabe gemeinsam unter vertauschten Bezeichnungen. Die `CLAUDE.md`-Baseline und btseee kamen später dazu und laufen nur im agentischen Benchmark: Dieser Bewerter beurteilt alle Bedingungen einer Aufgabe in einem Aufruf, eine neue Bedingung hätte hier jede Zahl verändert.

<p align="center">
  <img src="docs/assets/results-single-turn.svg" alt="Single-Turn-Suite. Qualitätsurteil: ohne Skill 7,6, dieser Skill 8,5, ub-mode 6,5, sickn33 7,2, ertugrul-dmr 6,7 auf 3 von 8 Aufgaben. Erfüllte Kriterien: ohne Skill 93,3 %, dieser Skill 99,2 %, ub-mode 95,0 %, sickn33 92,5 %, ertugrul-dmr 88,9 % auf 3 von 8 Aufgaben" width="760">
</p>

- **Ein starkes Modell kann das schon gut.** Ohne Skill erfüllt Sonnet 93,3 % der Kriterien. Ein Clean-Code-Skill kann wenig gewinnen und einiges verschlechtern.
- **Ein Skill kann schaden.** sickn33/clean-code fällt beim Hot Path auf 60 %, unter ohne Skill: Der Bit-Test wandert in eine Hilfsmethode innerhalb der Paket-Schleife, und die vage Exception bleibt. ertugrul-dmr fällt beim PR-Review auf 80 %, wo ohne Skill alles erfüllt.
- **Dieser Skill erfüllt in jeder Aufgabe mindestens so viele Kriterien wie ohne Skill** und hebt das durchschnittliche Qualitätsurteil von 7,6 auf 8,5. Sein einziger Fehler: ein nicht verlangter `currency`-Parameter in einem von drei Läufen.

Das ist eine Plausibilitätsprüfung, keine Rangliste: acht Fälle, die auch zur Verbesserung des Skills dienten, und ein KI-Bewerter, der die Antworten so sieht, wie sie geschrieben sind. Methode, Grenzen und alle Rohdaten: [`evals/README.md`](evals/README.md).

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

Der Skill lädt sich von selbst, sobald der Agent Code schreibt, ändert, korrigiert, refaktoriert oder testet, und bleibt bei Aufgaben ohne Code draußen. Direkt aufrufen geht mit `/clean-code <pfad>`, als Claude-Code-Plugin mit `/clean-code:clean-code <pfad>`. Soll er sicher immer gelten, auch bei Reviews, genügt eine Zeile in `CLAUDE.md` oder `AGENTS.md`; im Test oben lud sich damit jeder Skill in jedem Lauf:

```markdown
Before writing, changing or reviewing code, load the clean-code skill and follow it.
```

## Andere Clean-Code-Skills

Mehrere gute Skills behandeln dasselbe Buch mit anderen Zielen (Beschreibungen Stand November 2026; die gemessenen auf den Commits, die in [`evals/harness.py`](evals/harness.py) festgelegt sind):

| Skill | Ansatz | Hier gemessen |
|---|---|---|
| [unclebob/ub-mode](https://github.com/unclebob/ub-mode) | Robert C. Martins eigener kurzer Skill: make it work, make it right, follow practice. Wird mit `/ub-mode` eingeschaltet; seine Begleit-Tools (crapper, dryer, mutator) werden separat installiert | ja, die Skill-Datei ohne die Tools |
| [sickn33/agentic-awesome-skills → clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code) | Kompakte Zusammenfassung des Buchs in einer Datei, mit dem Hinweis, Repository-Konventionen zu folgen | ja |
| [ertugrul-dmr/clean-code-skills](https://github.com/ertugrul-dmr/clean-code-skills) | Ein Haupt-Skill pro Sprache (Python, TypeScript) plus sechs Themen-Skills: Namen, Funktionen, Kommentare, Tests, allgemeine Regeln, Pfadfinderregel | ja, auf den Python- und TypeScript-Aufgaben |
| [btseee/clean-code-skills](https://github.com/btseee/clean-code-skills) | Ein Skill für Clean Code und Clean Architecture mit Paketen für 21 Sprachen und 27 Frameworks, Skripten, die die Projektstruktur kartieren und Schichtgrenzen prüfen, und Befehlen für `init`, `audit`, `clean-up`, `plan` und `review`, die ein Projektgedächtnis in `.clean/` führen | ja, der ganze Skill-Ordner in normalen Sitzungen, ohne `init` (nur agentischer Benchmark) |
| [hatlesswizard/clean-code-skills](https://github.com/hatlesswizard/clean-code-skills) | 18 Skills, ein Prüfer pro Buchkapitel, plus ein Orchestrator | nein |
| [nghorbani/clean-code-skill](https://github.com/nghorbani/clean-code-skill) | Wissensbasis auf Abruf mit Glossar, Mustern und den Heuristiken G1–G36 | nein |
| [markoa/clean-code-skill](https://github.com/markoa/clean-code-skill) | Ein kurzer, verbindlicher Arbeitsvertrag aus 14 Regeln | nein |
| **dieses Repo** | Buch plus Vorrangregel, Scope-Disziplin, typische Agent-Fehler und ausdrückliche Ausnahmen, mit einer Beschreibung, die den Agent den Skill vor dem ersten Edit laden lässt | ja |

## Hinweis

Logo, Farbpalette und Gestaltungsregeln: [Focus-Branding](docs/branding/README.md).

Basiert auf *Clean Code* von Robert C. Martin (2008) und Kent Becks Regeln des einfachen Designs. Das Projekt ist weder mit den Autoren verbunden noch von ihnen autorisiert. Der Skill gibt die Ideen sinngemäß wieder; die Begründungen stehen im Buch.

Lizenz: [MIT](LICENSE)
