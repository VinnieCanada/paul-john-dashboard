"""
IntelOS — Master collection script.

Runs all configured collectors (meetings), writes to the database,
and classifies new meetings. Scheduled daily at 7am via Task Scheduler.

Usage:
    python scripts/intel/collect_all.py               # Run all collectors
    python scripts/intel/collect_all.py --meetings-only
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import init_db, write_meetings, get_meeting_stats


def run(meetings_only: bool = False):
    print(f"IntelOS collection starting at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    conn = init_db()

    # --- Meetings ---
    meeting_records = []

    try:
        from collect_fireflies import collect as collect_fireflies
        ff_meetings = collect_fireflies()
        if ff_meetings:
            meeting_records.extend(ff_meetings)
    except ImportError:
        pass
    except Exception as e:
        print(f"Fireflies error: {e}")

    if meeting_records:
        count = write_meetings(conn, meeting_records)
        print(f"Meetings: {count} records written to database")
    else:
        print("Meetings: no new records collected")

    try:
        from classify import classify_all
        classified = classify_all(conn)
        if classified:
            print(f"Classifier: {classified} meetings classified")
    except Exception as e:
        print(f"Classifier error: {e}")

    # --- Summary ---
    print("\n" + "=" * 60)
    stats = get_meeting_stats(conn)
    print(f"Database totals:")
    print(f"  Meetings:      {stats['total_meetings']}")
    print(f"  Team members:  {stats['team_members']}")
    if stats["latest_meeting_date"]:
        print(f"  Latest meeting: {stats['latest_meeting_date']}")
    print("=" * 60)

    conn.close()
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IntelOS — collect meetings")
    parser.add_argument("--meetings-only", action="store_true")
    args = parser.parse_args()
    run(meetings_only=args.meetings_only)
