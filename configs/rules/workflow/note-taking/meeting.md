# Notes: Meeting

Notes for recurring group meetings and ad-hoc discussions; stored under `<project-notes>/meetings/`.

---

## Scope

A meeting note captures what was discussed, decided, or assigned in a single meeting or a recurring series. It is the written record of the meeting, not a task list or a minutes document.

---

## Structure

```text
meetings/
├── <group>/  # one directory per recurring series
│   ├── README.md  # group name, cadence, participants, purpose
│   └── YYYY-MM-DD.md  # one file per session
└── ad-hoc/  # one-off meetings that do not belong to a series
    └── YYYY-MM-DD-<topic>.md  # one file per meeting
```

For recurring series, the `README.md` is the persistent reference; the session files are append-only records.

---

## What belongs here

| Belongs | Does not belong |
|---|---|
| What was discussed and by whom | Action items managed elsewhere (task tracker, issue) |
| Decisions reached in the meeting | Slides or supporting materials (link, do not embed) |
| Open questions raised | Background context that pre-dates the meeting |
| Follow-up commitments noted | Binding conventions (promote to `<rules>/`) |

---

## Session file format

Each session file should open with the date and attendees, then follow the meeting structure:

```markdown
# YYYY-MM-DD

**Attendees:** ...

## Topic 1
...

## Topic 2
...

## Follow-ups
- ...
```

Section headings are illustrative, not fixed: use functional names that fit the discussion (`## Discussion`, `## Decisions`, `## Open Questions`) instead of literal `## Topic 1`/`## Topic 2` where that reads more naturally. A reference table or a link to a related thread or note belongs in a session file when it is itself something the meeting produced or drew on directly (e.g. a vocabulary mapping worked out together, a pointer to the thread a decision affects); it does not license restating pre-existing background the meeting did not generate.

Keep entries factual. Record what was said and decided; do not editorialise. If a decision reached in a meeting becomes a binding convention, promote it to `<rules>/`.
