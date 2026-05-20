#!/usr/bin/env python3
"""Refresh the GTD dashboard from source files.

Recomputes project counts, action counts, waiting-for counts, and
rebuilds the dashboard summary sections.

Usage:
    python scripts/refresh_dashboard.py
"""

import re
from datetime import datetime, timedelta
from pathlib import Path


def find_workspace_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "gtd").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def count_active_projects(projects_text: str) -> int:
    count = 0
    in_archived = False
    for line in projects_text.splitlines():
        if line.strip().lower().startswith("## archived"):
            in_archived = True
        if line.startswith("### ") and not in_archived:
            count += 1
    return count


def count_unchecked(text: str) -> int:
    return len(re.findall(r"^- \[ \]", text, re.MULTILINE))


def count_waiting_for_active(wf_text: str) -> int:
    active_match = re.search(r"## Active\s*\n(.*?)(?=\n## |\Z)", wf_text, re.DOTALL)
    if not active_match:
        return 0
    return count_unchecked(active_match.group(1))


def build_project_summary(projects_text: str) -> str:
    lines = projects_text.splitlines()
    summary_lines = []
    current_area = None
    in_archived = False

    for line in lines:
        if line.startswith("## "):
            area_name = line[3:].strip()
            if area_name.lower() == "archived":
                in_archived = True
                continue
            in_archived = False
            current_area = area_name
            summary_lines.append(f"\n### {current_area}")
            continue

        if in_archived:
            continue

        if line.startswith("### ") and current_area:
            project_name = line[4:].strip()
            idx = lines.index(line)
            status_hint = ""
            for check_line in lines[idx + 1: idx + 6]:
                if check_line.strip().startswith("- **Status:**"):
                    status_text = check_line.split("**Status:**")[1].strip()
                    status_hint = status_text[:80]
                    break
            is_complete = "complete" in status_hint.lower()
            checkbox = "[x]" if is_complete else "[ ]"
            hint = f" -> {status_hint}" if status_hint else ""
            summary_lines.append(f"- {checkbox} {project_name}{hint}")

    if not any(line.startswith("- ") for line in summary_lines):
        summary_lines.append("\n_(No active projects yet)_")

    return "\n".join(summary_lines)


def build_waiting_for_summary(wf_text: str) -> str:
    active_match = re.search(r"## Active\s*\n(.*?)(?=\n## |\Z)", wf_text, re.DOTALL)
    if not active_match:
        return "_(Nothing delegated yet)_"

    active_section = active_match.group(1)
    items = re.findall(r"^- \[ \] (.+)$", active_section, re.MULTILINE)

    if not items:
        return "_(Nothing delegated yet)_"

    today = datetime.now().date()
    summary_lines = []

    for item in items:
        date_match = re.search(r"Requested:\s*(\d{4}-\d{2}-\d{2})", item)
        age_str = ""
        warning = ""
        if date_match:
            req_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            age_days = (today - req_date).days
            age_str = f" ({age_days}d)"
            if age_days > 5:
                warning = " !!!"
        desc = item[:60] + "..." if len(item) > 60 else item
        summary_lines.append(f"- [ ] {desc}{age_str}{warning}")

    return "\n".join(summary_lines)


def refresh_dashboard(workspace_dir: Path) -> str:
    gtd_dir = workspace_dir / "gtd"

    projects_text = (gtd_dir / "projects.md").read_text(encoding="utf-8")
    actions_text = (gtd_dir / "next-actions.md").read_text(encoding="utf-8")
    wf_text = (gtd_dir / "waiting-for.md").read_text(encoding="utf-8")
    dashboard_text = (gtd_dir / "dashboard.md").read_text(encoding="utf-8")

    project_count = count_active_projects(projects_text)
    action_count = count_unchecked(actions_text)
    wf_count = count_waiting_for_active(wf_text)

    dashboard_text = re.sub(
        r"\*\*Projects:\*\* \d+ active",
        f"**Projects:** {project_count} active",
        dashboard_text,
    )
    dashboard_text = re.sub(
        r"\*\*Next Actions:\*\* \d+ defined",
        f"**Next Actions:** {action_count} defined",
        dashboard_text,
    )
    dashboard_text = re.sub(
        r"\*\*Waiting For:\*\* \d+ items",
        f"**Waiting For:** {wf_count} items",
        dashboard_text,
    )

    project_summary = build_project_summary(projects_text)
    dashboard_text = re.sub(
        r"(## Active Projects by Area\s*\n).*?(?=\n---)",
        f"\\1{project_summary}\n",
        dashboard_text,
        flags=re.DOTALL,
    )

    wf_summary = build_waiting_for_summary(wf_text)
    dashboard_text = re.sub(
        r"(## Waiting For \(Active\)\s*\n).*?(?=\n---|\Z)",
        f"\\1\n{wf_summary}\n",
        dashboard_text,
        flags=re.DOTALL,
    )

    (gtd_dir / "dashboard.md").write_text(dashboard_text, encoding="utf-8")
    return f"Dashboard refreshed: {project_count} projects, {action_count} actions, {wf_count} waiting-for"


if __name__ == "__main__":
    workspace = find_workspace_root()
    result = refresh_dashboard(workspace)
    print(result)
