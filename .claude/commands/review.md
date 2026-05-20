# Review

> Guided weekly GTD review for Vinya. Processes inbox, walks through all lists, scans areas and someday-maybe, rebuilds the dashboard. Run weekly — Fridays recommended. Target: 30-60 minutes.

---

## Instructions

You are running a **GTD weekly review** with Vinya. This keeps the system trustworthy. Follow the phases interactively — don't rush.

---

## Phase 1: Load Context

Read all GTD files:
1. `gtd/dashboard.md`
2. `gtd/inbox.md`
3. `gtd/projects.md`
4. `gtd/next-actions.md`
5. `gtd/waiting-for.md`
6. `gtd/someday-maybe.md`
7. `gtd/areas.md`
8. `gtd/review-checklist.md`
9. `context/outreach.md` — check pipeline status

---

## Phase 2: GET CLEAR

**Goal:** Empty all inboxes and capture everything floating in your head.

### 2.1 Process Inbox
1. Read `gtd/inbox.md`
2. If items exist, walk through each using the GTD decision tree
3. Route each item to the correct file
4. Empty inbox to zero

### 2.2 Mind Sweep
1. Go through trigger categories from `gtd/review-checklist.md`
2. Ask: "Any open loops here?" for each category
3. Capture anything new to inbox, then process it

**STOP and confirm before proceeding to Phase 3.**

---

## Phase 3: GET CURRENT

**Goal:** All lists reflect reality. Every project has a next action.

### 3.1 Review Calendar
- Past week: any follow-ups needed?
- Next 2 weeks: any prep needed?

### 3.2 Walk Through Next Actions
- Present each context section from `gtd/next-actions.md`
- For each: "Done? Still relevant? Needs updating?"

### 3.3 Walk Through Waiting For
- Present each item from `gtd/waiting-for.md`
- Flag anything overdue — suggest follow-up action
- Check `context/outreach.md` — any follow-ups due?

### 3.4 Walk Through Projects
- Present each project from `gtd/projects.md`
- For each: "Still active? Progress? Status change?"
- **Stuck project test:** Does every project have at least one next action?

**STOP and confirm before proceeding to Phase 4.**

---

## Phase 4: GET CREATIVE

**Goal:** Look up and out.

### 4.1 Scan Someday/Maybe
- "Anything ready to activate? Anything to delete? New ideas?"

### 4.2 Scan Areas
- Any area being neglected? Any area missing a project?

### 4.3 Open Brainstorm
- "Any big-picture ideas or strategic thoughts from this review?"

---

## Phase 5: REBUILD

1. Run `python scripts/refresh_dashboard.py` to recompute counts
2. Update Flagged/Urgent section if needed
3. Set "Last Review" to today's date
4. Set "Next Review" to one week from today
5. Report summary

---

## Critical Rules

- **Interactive** — Present lists, ask questions, wait for responses
- **Don't skip phases** — GET CLEAR before GET CURRENT before GET CREATIVE
- **Specific actions** — "Think about pricing" is not an action. "Draft three pricing tiers in a doc" is.
- **Every project needs a next action**
- **Update files as you go**
- **Time-box** — If a topic goes deep, capture it and move on
