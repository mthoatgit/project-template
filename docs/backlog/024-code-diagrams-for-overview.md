---
type: improvement
---

# P2 · Diagramm-Skill für Code-Überblick (Packages, Kernprozesse, Entscheidungen)

- **Symptom.** Es gibt keinen strukturierten Weg, sich in einer (AI-generierten) Codebasis schnell zu orientieren. ADRs existieren (`docs/adr/`), sind aber reiner Text ohne visuellen Anker; ein Package-Überblick oder Ablaufdiagramme der Kernprozesse werden aktuell gar nicht erzeugt.
- **Impact.** Gerade wenn Code von Claude statt vom Menschen geschrieben wird, ist der schnelle Wiedereinstieg ("was gibt es, wie hängt es zusammen, warum ist es so gebaut") wichtiger als bei selbst geschriebenem Code. Ohne das kostet jede Rückkehr zu einem Projekt (oder Review) mehr Zeit, weil die Landkarte fehlt.
- **Proposed shape.** Aus Chat-Diskussion (2026-07-18) destilliert:
  - Diagrammformat: **Mermaid** (kein PlantUML) — rendert nativ in GitHub, VS Code und Claude-Artifacts, keine zusätzliche Rendering-Pipeline.
  - Genau 2 Diagrammarten, bewusst kein vollständiges UML/Audit-Set:
    1. **Package-Abhängigkeitsdiagramm** statt Komponenten-/Container-Diagramm (C4 Level 2) — bei Ein-Anwendungs-Setups (Standardfall hier) ist die relevante Ebene C4 Level 3, und "Components" entsprechen bei Java direkt den fachlichen Packages. Gehört inhaltlich in `workflow-architecture` (ergänzt `system-design.md`).
    2. **Sequenz-/Flowcharts für die 3–5 Kernprozesse** (Einstiegspunkte, Happy-Path durch den Code) — on-demand, nicht phasengebunden.
  - Explizit ausgeschlossen: vollständige Klassendiagramme (hoher Pflegeaufwand, wenig Verständnis-Mehrwert außerhalb von Audit-Anforderungen).
  - Struktur-Entscheidung: **kein Skill pro Diagrammtyp** (Redundanz bei Ablageort/Namenskonvention/Stil). Stattdessen ein Skill mit Modi (z.B. `/diagram package`, `/diagram flow <thema>`), gemeinsame Klammer für Konventionen, pro Modus eigener spezifischer Abschnitt.
  - Entscheidungen sichtbar machen: kein neues Diagrammformat dafür, sondern (a) ADR-Index-Tabelle (analog `docs/tasks/index.md`) mit ID/Status/Datum/Ein-Satz-Zusammenfassung, (b) Querverweise `(siehe ADR-XXX)` direkt im Package-Diagramm / bei Kernprozessen.
  - Kadenz: nicht pro Task neu zeichnen — Refresh-Check am Epic-Ende (wo ohnehin reflektiert wird), sonst on-demand.
- **Source.** Chat-Session 2026-07-18 (keine Projekt-spezifische Codebasis, generelle Überlegung zur Verständlichkeit von AI-generiertem Code). Noch nicht besprochen: genauer Skill-Name, ob Erweiterung von `workflow-architecture` oder eigener Skill, Trigger-Wortliste.
