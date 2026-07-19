---
type: improvement
---

# P1 · Workflow-overview.md driftet unbemerkt — Sync-Trigger unreliable

- **Symptom.** Der Sync-Mechanismus für `docs/workflow-overview.md` ist halb-automatisch. Der `/sync-workflow-diagram` Command selbst funktioniert richtig — er liest die Source-of-Truth (`~/.claude/CLAUDE.md`, alle skills, alle commands), vergleicht gegen den Diagram-Zustand, updated bei Drift, committed und pusht. **Der Aufruf passiert aber nicht automatisch.** Einziger Trigger heute: PostToolUse-Hook in `settings.json` der bei Edits auf `workflow-*/SKILL.md` eine Reminder-Nachricht in Claude's Context injiziert — ein weicher Hinweis, keine Ausführung. Claude befolgt ihn oft nicht. Non-Claude-Edits (IDE, direktes git commit von dir) triggern gar nichts. Beweis: heute in dieser Session wurden 4 Drifts entdeckt, die seit ~2 Tagen unadressiert waren (Item-021-Layout-Umbau: `docs/tasks/epics/` → `docs/tasks/E<N>/`, `orchestrator.py` → `python -m orchestrator`, workflow-bugs neu, Golden Rule "or bug").
- **Impact.** workflow-overview.md driftet unbemerkt vom tatsächlichen Workflow. Mermaid-Diagramme zeigen alte Pfade, Phase-Reference-Tabelle nennt gedroppte Commands, Golden Rules verpassen neue Regeln. Als Cold-Start-Referenz für Sessions und für dich beim Nachschauen ist die Datei damit nur bedingt vertrauenswürdig — man muss immer gegenprüfen. Divergenz-Kosten wachsen unsichtbar bis jemand sie manuell entdeckt. Der Zweck einer "quick-recall reference" ist damit strukturell erodiert.
- **Proposed shape.** Session 2026-07-11 hat drei Pfade diskutiert und klar zu **Path 1** tendiert:
  - **Path 1 (empfohlen): Lokaler post-commit Git-Hook in `~/.claude/`.** Script an `~/.claude/.git/hooks/post-commit`, feuert nach jedem git commit auf dotfiles-claude. Prüft ob workflow-relevante Files (`CLAUDE.md`, `skills/workflow-*/`, `commands/`, `rules/`) im Commit waren. Wenn ja: startet `claude -p "/sync-workflow-diagram"` im Hintergrund, redirect nach Log-File. **Nutzt lokale Subscription-Auth via `claude` CLI — kein API Key, keine Extra-Kosten.** Draft-Script fertig (siehe Session-Kontext), NICHT installiert. Grenze: der Hook lebt in `.git/hooks/` und ist damit nicht versioniert — für Multi-Machine bräuchte es zusätzlich einen Installer-Script.
  - **Path 2a: GitHub Actions Workflow mit headless Claude.** Cross-Repo push via Deploy Key (SSH-Keypair per `gh` CLI installierbar auf beiden Repos). Braucht **zusätzlich** `ANTHROPIC_API_KEY` als weiteres Secret — die Claude Code Subscription deckt Actions-Nutzung NICHT ab (per Docs-Check in dieser Session verifiziert). Kosten: pay-as-you-go pro Run, geschätzt ~$1-4/Monat bei realistischer Rate. Multi-Machine-Coverage voll gegeben. Session verwarf wegen Setup-Overhead + laufende Extra-Kosten trotz existierender Subscription.
  - **Path 2c: Actions mit mechanic-only Check.** Wie 2a, aber ohne headless Claude — Shell/Python-Script prüft nur exakte String-Matches (Pfade, Command-Namen). Bei Verdacht auf semantische Drift wird GitHub Issue geöffnet statt zu editieren. Zero API-Kosten, aber ~75% Coverage (der heutige "Golden Rule 'or bug'" Fix wäre durchgerutscht). Kompromiss, in der Session unter Path 1 unattraktiv.
- **Source.** 2026-07-11 spät in Session — bei Prüfung ob der RFC-2119-Style-Pass auch `workflow-overview.md` betrifft, entdeckt dass die Datei seit ~2 Tagen driftet ohne dass der aktuelle Reminder-Mechanismus greift. Nach `/sync-workflow-diagram` Manual-Run und 4 Drift-Fixes: Diskussion zu Path 1/2/2c. User: *"mache eine notiz im backlog und prio1 direkt erst als erstes morgen"*.

## Session-Kontext — Wiedereinstiegspunkt für nächste Session

**Status:** Path-1-Design fertig, Draft-Script vorhanden (siehe unten), NICHT installiert. Nichts an settings.json oder Hooks in dieser Session geändert.

**Was schon geklärt ist (nicht neu diskutieren):**
- Aktueller Mechanismus (`/sync-workflow-diagram` Command + PostToolUse-Hook Reminder) ist unreliable. Beweis: 4 Drifts saßen unentdeckt.
- Subscription-Auth funktioniert für lokales `claude -p` — kein API Key nötig für Path 1.
- Subscription-Auth funktioniert NICHT für GitHub Actions Runner. Docs-Check bestätigt: *"Add ANTHROPIC_API_KEY to your repository secrets"* + *"API costs: Each Claude interaction consumes API tokens"*. Path 2a würde ~$1-4/Monat Extra kosten trotz Subscription.
- Path 1 ist der Sweet-Spot: 0 Kosten, ~15 min Install, deckt Single-Machine ab. Cross-Machine später via Installer-Script möglich.

**Draft des post-commit Hook Scripts** (aus der Session, unverändert übernehmen):

```sh
#!/bin/sh
# Post-commit hook: keep project-template/docs/workflow-overview.md
# in sync with ~/.claude/ workflow files.
# Uses local subscription auth via `claude -p` — no API key required.

set -e

# Bail-outs
command -v claude >/dev/null 2>&1 || exit 0
[ -d "$HOME/dev/project-template" ] || exit 0

CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null || true)

# Only fire when a workflow-affecting file changed
echo "$CHANGED" | grep -qE '^(CLAUDE\.md|skills/workflow-|commands/|rules/)' || exit 0

LOG="$HOME/.claude/.sync-hook.log"
(
  echo "=== $(date -u '+%Y-%m-%d %H:%M:%S UTC') post-commit sync triggered ==="
  echo "Changed:"
  echo "$CHANGED"
  echo "---"
  claude -p "/sync-workflow-diagram" 2>&1
  echo "=== done ==="
  echo
) >> "$LOG" 2>&1 &

exit 0
```

**Konkrete erste Schritte für nächste Session:**

1. **Hook installieren** — Script nach `~/.claude/.git/hooks/post-commit` schreiben, `chmod +x`, smoke-testen mit einem dummy-Commit. Zwei Test-Cases: (a) Commit der KEINEN workflow-relevanten File anfasst → sollte silent exit (kein Log-Eintrag); (b) Commit der z.B. `CLAUDE.md` anfasst → sollte im `~/.claude/.sync-hook.log` einen "sync triggered" Eintrag erzeugen.
2. **Verify Log-Handling** — `~/.claude/.sync-hook.log` ist durch existierende `*.log` Blacklist in `.gitignore` schon gitignored (verifiziert). Log wächst aber unbegrenzt — entweder als "manuelle Trunkation bei Bedarf" akzeptieren, oder ein simples Head-Cap ins Script einbauen (`tail -n 5000` Rotate-Pattern). Deine Entscheidung.
3. **Optional: Installer-Script für Multi-Machine-Bereitschaft** — Path 3 aus der Diskussion. Versioniertes `~/.claude/hooks/post-commit` als Master (in dotfiles-claude committed), plus `~/.claude/bin/install-hooks.sh` das nach `.git/hooks/` copyt. Nach jedem Clone einmal laufen lassen. ~30 min extra Aufwand. Vorschlag: **nicht in dieser Session, aufheben bis Multi-Machine relevant wird**.
4. **PostToolUse-Hook in settings.json diskutieren** — mit Path 1 aktiv wird der SKILL.md-Reminder in settings.json weitgehend redundant (git commit triggert die Sync eh). Optionen: (a) löschen (deine Minimalism-Regel), (b) als Belt-and-suspenders behalten (feuert vor commit → hilft evtl. in laufender Session), (c) Matcher auf CLAUDE.md/commands/rules erweitern für maximalen Vorher-Reminder. Entscheiden.

**Nicht vergessen (Nebenfund):**
- `~/.claude/commands/start-epic.md` (Zeile 14) und `~/.claude/commands/ship-epic.md` (Zeile 17) verweisen noch auf gedroppten `docs/tasks/epics/E<N>/T<NN>-*.md` Pfad — sind selbst stale und werden **von keinem Sync-Mechanismus abgedeckt** (weder aktuell noch Path 1 — der syncht ja nur `workflow-overview.md`, nicht die commands selbst). Kein Blocker für Path-1-Install, aber gehört ins gleiche Konsistenz-Gefühl. Entweder in derselben Session mitfixen (2-min Edit) oder eigenes P2-Backlog-Item.
- Diese Datei nach Umsetzung: Status `done`, Move nach `topics/archive/`, README-Callout entfernen.
