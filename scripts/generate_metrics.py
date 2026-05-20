"""
DataOS — Key Metrics Generator

Reads the database and generates key-metrics.md in context/group/.
This file is loaded by /prime so your AI always has fresh data.

Usage:
    python scripts/generate_metrics.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "data.db"
OUTPUT_PATH = WORKSPACE_ROOT / "context" / "key-metrics.md"


def fmt_number(value, prefix="", suffix=""):
    if value is None:
        return "No data"
    if isinstance(value, float):
        return f"{prefix}{value:,.0f}{suffix}"
    return f"{prefix}{value:,}{suffix}"


def fmt_currency(value, symbol="$"):
    if value is None:
        return "No data"
    return f"{symbol}{value:,.0f}"


def fmt_pct(value):
    if value is None:
        return "No data"
    return f"{value:.1f}%"


def query_one(conn, sql):
    try:
        row = conn.execute(sql).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def query_all(conn, sql):
    try:
        return [dict(r) for r in conn.execute(sql).fetchall()]
    except Exception:
        return []


def table_exists(conn, name):
    r = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return r is not None


# ============================================================
# SECTION GENERATORS
# Each function returns a list of markdown lines for its section.
# Add new section functions here as you connect more data sources.
# ============================================================


def section_fx_rates(conn):
    if not table_exists(conn, "fx_rates"):
        return []
    lines = ["## Exchange Rates", "| Currency | Rate (from USD) | As Of |",
             "|----------|----------------|-------|"]
    rows = query_all(conn, """
        SELECT date, currency, rate FROM fx_rates
        WHERE date = (SELECT MAX(date) FROM fx_rates)
        ORDER BY currency
    """)
    for r in rows:
        lines.append(f"| {r['currency']} | {r['rate']:.4f} | {r['date']} |")
    lines.append("")
    return lines


# --- Add new section functions below as you connect data sources ---
# Examples:
#   def section_stripe(conn): ...
#   def section_outreach(conn): ...
#   def section_google_analytics(conn): ...


# Register all active section functions here
SECTIONS = [
    section_fx_rates,
    # section_stripe,
    # section_outreach,
    # section_google_analytics,
]


def generate(conn):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Key Metrics",
        "",
        f"> Auto-generated from database. Last updated: {today}",
        f"> Source: `data/data.db` | Regenerate: `python scripts/generate_metrics.py`",
        "",
    ]

    for section_fn in SECTIONS:
        try:
            section_lines = section_fn(conn)
            if section_lines:
                lines.extend(section_lines)
        except Exception as e:
            lines.append(f"<!-- Error in {section_fn.__name__}: {e} -->")
            lines.append("")

    lines.append("## Data Freshness")
    lines.append("| Source | Latest Record | Status |")
    lines.append("|--------|---------------|--------|")

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name != 'collection_log' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()

    for t in tables:
        name = t["name"]
        try:
            row = conn.execute(f"SELECT MAX(date) as d FROM {name}").fetchone()
            if row and row["d"]:
                lines.append(f"| {name} | {row['d']} | Connected |")
            else:
                lines.append(f"| {name} | — | Empty |")
        except Exception:
            lines.append(f"| {name} | — | No date column |")

    lines.append("")
    return "\n".join(lines)


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run collection first: python scripts/collect.py")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    content = generate(conn)
    conn.close()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Key metrics written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
