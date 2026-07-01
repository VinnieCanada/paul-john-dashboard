"""AIOS Workspace Dashboard — Vinya"""

import re
import sqlite3
from datetime import datetime, date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="AIOS Dashboard", layout="wide")
st.title("AIOS Workspace")
st.caption(f"Vinya — {date.today().strftime('%B %d, %Y')}")

# ── Pipeline ──────────────────────────────────────────────────────────────────

def parse_outreach():
    text = (ROOT / "context" / "outreach.md").read_text(encoding="utf-8")
    metrics = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*(.+?)\s*\|\s*(\d+)\s*\|", line)
        if m:
            metrics[m.group(1).strip()] = int(m.group(2))
    leads = []
    in_pipeline = False
    for line in text.splitlines():
        if line.strip().startswith("## Pipeline"):
            in_pipeline = True
            continue
        if in_pipeline and line.startswith("## "):
            break
        if in_pipeline and line.startswith("| ") and "---" not in line and "Name" not in line and line.strip() != "|":
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 6 and parts[0]:
                leads.append(parts)
    return metrics, leads


st.header("Pipeline")
metrics, leads = parse_outreach()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", metrics.get("Total leads identified", 0))
col2.metric("Won", metrics.get("Won (clients)", 0))
col3.metric("Active Conversations", metrics.get("Active conversations", 0))
col4.metric("Proposals Out", metrics.get("Proposals sent", 0))

if leads:
    st.subheader("Active Clients")
    for lead in leads:
        name, company, type_, status, last_contact, next_action = lead[:6]
        notes = lead[6] if len(lead) > 6 else ""
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 1, 3])
            c1.markdown(f"**{name}** — {company} _{type_}_")
            c2.markdown(f"`{status}`")
            c3.markdown(f"Next: {next_action}")
            if notes:
                st.caption(notes)
else:
    st.info("No leads yet — add contacts from your network.")

st.divider()

# ── GTD ───────────────────────────────────────────────────────────────────────

def count_unchecked(text):
    return len(re.findall(r"^- \[ \]", text, re.MULTILINE))

def count_active_projects(text):
    count = 0
    in_archived = False
    for line in text.splitlines():
        if line.strip().lower().startswith("## archived"):
            in_archived = True
        if line.startswith("### ") and not in_archived:
            count += 1
    return count

def count_waiting_for_active(text):
    m = re.search(r"## Active\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return count_unchecked(m.group(1)) if m else 0

gtd = ROOT / "gtd"
projects_text = (gtd / "projects.md").read_text(encoding="utf-8")
actions_text = (gtd / "next-actions.md").read_text(encoding="utf-8")
wf_text = (gtd / "waiting-for.md").read_text(encoding="utf-8")
inbox_text = (gtd / "inbox.md").read_text(encoding="utf-8")

project_count = count_active_projects(projects_text)
action_count = count_unchecked(actions_text)
wf_count = count_waiting_for_active(wf_text)
inbox_count = count_unchecked(inbox_text)

st.header("GTD System")
g1, g2, g3, g4 = st.columns(4)
g1.metric("Active Projects", project_count)
g2.metric("Next Actions", action_count)
g3.metric("Waiting For", wf_count)
g4.metric("Inbox Items", inbox_count, delta="needs processing" if inbox_count > 0 else None, delta_color="inverse")

st.divider()

# ── Meetings ──────────────────────────────────────────────────────────────────

st.header("Recent Meetings")
intel_db = ROOT / "data" / "intel.db"

if intel_db.exists():
    conn = sqlite3.connect(intel_db)
    rows = conn.execute(
        "SELECT title, date, participants, summary FROM meetings ORDER BY date DESC LIMIT 5"
    ).fetchall()
    conn.close()

    if rows:
        for title, meeting_date, participants, summary in rows:
            with st.expander(f"**{title}** — {meeting_date}"):
                if participants:
                    import json
                    try:
                        people = json.loads(participants)
                        emails = [p.get("email", "") for p in people if p.get("email")]
                        st.caption("Attendees: " + ", ".join(emails))
                    except Exception:
                        st.caption(participants)
                if summary:
                    st.markdown(summary[:500] + ("..." if len(summary or "") > 500 else ""))
                else:
                    st.caption("No summary available.")
    else:
        st.info("No meetings recorded yet.")
else:
    st.info("Intel database not found.")

st.divider()

# ── Key Metrics ───────────────────────────────────────────────────────────────

st.header("Key Metrics")
data_db = ROOT / "data" / "data.db"

if data_db.exists():
    conn = sqlite3.connect(data_db)
    rows = conn.execute(
        "SELECT currency, rate, date FROM fx_rates ORDER BY date DESC, currency ASC"
    ).fetchall()
    conn.close()

    if rows:
        latest_date = rows[0][2]
        age = (date.today() - datetime.strptime(latest_date, "%Y-%m-%d").date()).days
        freshness = "Fresh" if age <= 1 else f"Stale ({age}d old)"
        color = "green" if age <= 1 else "orange" if age <= 3 else "red"

        seen = set()
        latest_rates = []
        for currency, rate, d in rows:
            if currency not in seen:
                seen.add(currency)
                latest_rates.append((currency, rate, d))

        st.caption(f"FX Rates — :{color}[{freshness}] as of {latest_date}")
        cols = st.columns(len(latest_rates))
        for i, (currency, rate, _) in enumerate(latest_rates):
            cols[i].metric(f"USD → {currency}", f"{rate:.4f}")
    else:
        st.info("No FX data yet.")
else:
    st.info("Data database not found.")
