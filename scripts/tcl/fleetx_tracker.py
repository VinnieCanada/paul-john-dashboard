#!/usr/bin/env python3
"""
TCL Fleetx Live Truck Tracker
Logs into Ishan's Fleetx account and pulls real-time truck locations.

Uses browser automation — no API key needed, just his existing login.

Quick start:
  1. Add to .env:
       FLEETX_EMAIL=ishan@tcllogistics.com
       FLEETX_PASSWORD=his-fleetx-password
  2. pip install playwright python-dotenv
     playwright install chromium
  3. python scripts/tcl/fleetx_tracker.py

Options:
  --headless     Run without opening a browser window (for scheduled runs)
  --json         Output raw JSON instead of formatted report
  --vehicle REG  Filter to a specific truck (e.g. --vehicle MH01AB1234)
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FLEETX_EMAIL = os.getenv("FLEETX_EMAIL")
FLEETX_PASSWORD = os.getenv("FLEETX_PASSWORD")

# Fleetx web app — these URLs are standard for Fleetx customers
FLEETX_APP = "https://app.fleetx.io"
LIVE_TRACKING_PATHS = [
    "/live-tracking",
    "/vehicles/live",
    "/tracking/live",
    "/dashboard",
]

# Keywords that identify vehicle/tracking API calls
TRACKING_KEYWORDS = [
    "vehicle", "truck", "tracking", "location", "live", "fleet",
    "gps", "trip", "route", "telematics"
]


async def run_tracker(headless: bool = False, vehicle_filter: str = None):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("\nPlaywright not installed. Run:")
        print("  pip install playwright && playwright install chromium\n")
        sys.exit(1)

    trucks = []
    api_endpoints_found = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        page = await context.new_page()

        # --- Intercept API calls the Fleetx app makes internally ---
        async def capture_api_response(response):
            url = response.url
            if any(k in url.lower() for k in TRACKING_KEYWORDS):
                try:
                    content_type = response.headers.get("content-type", "")
                    if "json" in content_type:
                        data = await response.json()
                        api_endpoints_found[url] = data
                except Exception:
                    pass

        page.on("response", capture_api_response)

        # --- Login ---
        print("Connecting to Fleetx...")
        await page.goto(FLEETX_APP, wait_until="domcontentloaded", timeout=30000)

        # Handle login page
        current_url = page.url
        if any(x in current_url for x in ["login", "signin", "auth"]):
            print("Logging in...")
            await _do_login(page)
        else:
            # May already be logged in (saved session) or need to detect login form
            login_form = await page.query_selector('input[type="password"]')
            if login_form:
                print("Logging in...")
                await _do_login(page)

        print(f"Logged in. Current page: {page.url}")

        # --- Navigate to live tracking ---
        print("Loading live tracking data...")
        tracking_loaded = False

        for path in LIVE_TRACKING_PATHS:
            try:
                await page.goto(f"{FLEETX_APP}{path}", wait_until="networkidle", timeout=20000)
                await asyncio.sleep(4)  # Let map and API calls settle
                tracking_loaded = True
                print(f"Tracking page: {FLEETX_APP}{path}")
                break
            except Exception:
                continue

        if not tracking_loaded:
            # Fall back to dashboard and wait for data
            await page.goto(FLEETX_APP, wait_until="networkidle", timeout=20000)
            await asyncio.sleep(5)

        # --- Extract vehicle data ---

        # Method 1: From intercepted API calls
        trucks = _parse_api_responses(api_endpoints_found)

        # Method 2: From page DOM if API interception didn't work
        if not trucks:
            trucks = await _extract_from_dom(page)

        await browser.close()

    return trucks, api_endpoints_found


async def _do_login(page):
    """Fill and submit the Fleetx login form."""
    # Try common selector patterns for email/phone input
    email_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[placeholder*="email" i]',
        'input[placeholder*="mobile" i]',
        'input[placeholder*="phone" i]',
        'input[name="username"]',
    ]
    password_selectors = [
        'input[type="password"]',
        'input[name="password"]',
    ]
    submit_selectors = [
        'button[type="submit"]',
        'button:has-text("Login")',
        'button:has-text("Sign in")',
        'button:has-text("Log in")',
    ]

    for sel in email_selectors:
        try:
            await page.fill(sel, FLEETX_EMAIL, timeout=3000)
            break
        except Exception:
            continue

    for sel in password_selectors:
        try:
            await page.fill(sel, FLEETX_PASSWORD, timeout=3000)
            break
        except Exception:
            continue

    for sel in submit_selectors:
        try:
            await page.click(sel, timeout=3000)
            break
        except Exception:
            continue

    await page.wait_for_load_state("networkidle", timeout=20000)


def _parse_api_responses(api_data: dict) -> list:
    """Extract truck records from intercepted Fleetx API responses."""
    trucks = []

    for url, data in api_data.items():
        # Fleetx returns vehicle lists in various shapes — try common structures
        candidates = []

        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict):
            for key in ["vehicles", "data", "trucks", "results", "items", "fleet"]:
                if key in data and isinstance(data[key], list):
                    candidates = data[key]
                    break

        for item in candidates:
            if not isinstance(item, dict):
                continue

            # Check if this looks like a vehicle record
            has_location = any(k in item for k in ["lat", "latitude", "lng", "longitude", "coordinates"])
            has_identity = any(k in item for k in ["registration", "vehicle_no", "reg_no", "name", "number"])

            if has_location or has_identity:
                truck = _normalize_vehicle(item)
                if truck:
                    trucks.append(truck)

    # Deduplicate by registration
    seen = set()
    unique = []
    for t in trucks:
        key = t.get("registration", t.get("name", ""))
        if key and key not in seen:
            seen.add(key)
            unique.append(t)

    return unique


def _normalize_vehicle(raw: dict) -> dict:
    """Normalize a raw Fleetx vehicle object to a standard shape."""
    return {
        "registration": raw.get("registration") or raw.get("vehicle_no") or raw.get("reg_no") or raw.get("name") or "Unknown",
        "lat": raw.get("latitude") or raw.get("lat") or raw.get("last_lat"),
        "lng": raw.get("longitude") or raw.get("lng") or raw.get("last_lng"),
        "speed_kmh": raw.get("speed") or raw.get("vehicle_speed") or 0,
        "status": raw.get("status") or raw.get("vehicle_status") or ("MOVING" if (raw.get("speed") or 0) > 5 else "STOPPED"),
        "driver": raw.get("driver_name") or raw.get("driver") or "—",
        "last_updated": raw.get("timestamp") or raw.get("last_updated") or raw.get("updated_at") or "—",
        "trip_id": raw.get("trip_id") or raw.get("current_trip_id") or "—",
        "destination": raw.get("destination") or raw.get("end_address") or "—",
    }


async def _extract_from_dom(page) -> list:
    """Fallback: try to pull vehicle info directly from the page DOM."""
    trucks = []

    selectors = [
        ".vehicle-list-item",
        ".vehicle-item",
        "[data-vehicle-id]",
        ".truck-row",
        ".fleet-item",
    ]

    for sel in selectors:
        items = await page.query_selector_all(sel)
        if items:
            print(f"Found {len(items)} vehicle elements via DOM ({sel})")
            for item in items:
                text = await item.inner_text()
                trucks.append({"raw_text": text.strip(), "source": "dom"})
            break

    return trucks


def _maps_link(lat, lng) -> str:
    if lat and lng:
        return f"https://maps.google.com/?q={lat},{lng}"
    return "Location unavailable"


def print_report(trucks: list, api_calls: dict, vehicle_filter: str = None):
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    print(f"\n{'═'*58}")
    print(f"  TCL FLEET STATUS   {now}")
    print(f"{'═'*58}")

    if not trucks:
        print("\n  No vehicle data captured from Fleetx.")
        print("\n  Possible reasons:")
        print("  • Login failed — check FLEETX_EMAIL and FLEETX_PASSWORD in .env")
        print("  • Tracking page URL is different for Ishan's account")
        print("  • Fleetx updated their web app structure")
        print(f"\n  API calls captured ({len(api_calls)} total):")
        for url in list(api_calls.keys())[:10]:
            print(f"    {url}")
        return

    if vehicle_filter:
        trucks = [t for t in trucks if vehicle_filter.upper() in t.get("registration", "").upper()]

    moving = [t for t in trucks if (t.get("speed_kmh") or 0) > 5]
    stopped = [t for t in trucks if (t.get("speed_kmh") or 0) <= 5]

    print(f"\n  Total trucks: {len(trucks)}  |  Moving: {len(moving)}  |  Stopped: {len(stopped)}\n")
    print(f"{'─'*58}")

    for t in trucks:
        speed = t.get("speed_kmh") or 0
        status_icon = "🚛" if speed > 5 else "🅿"
        status_label = f"MOVING  {speed} km/h" if speed > 5 else "STOPPED"
        reg = t.get("registration", "Unknown")
        driver = t.get("driver", "—")
        destination = t.get("destination", "—")
        maps = _maps_link(t.get("lat"), t.get("lng"))
        last_update = t.get("last_updated", "—")

        print(f"  {status_icon}  {reg}")
        print(f"     Status    : {status_label}")
        if driver != "—":
            print(f"     Driver    : {driver}")
        if destination != "—":
            print(f"     Going to  : {destination}")
        print(f"     Map       : {maps}")
        print(f"     Updated   : {last_update}")
        print(f"{'─'*58}")

    print(f"\n  Run again any time for a fresh update.\n")


def main():
    parser = argparse.ArgumentParser(description="TCL Fleetx Truck Tracker")
    parser.add_argument("--headless", action="store_true", help="Run without browser window")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output raw JSON")
    parser.add_argument("--vehicle", help="Filter by vehicle registration (e.g. MH01AB1234)")
    args = parser.parse_args()

    # Credential check
    if not FLEETX_EMAIL or not FLEETX_PASSWORD:
        print("\nMissing Fleetx credentials. Add these to your .env file:\n")
        print("  FLEETX_EMAIL=ishan@tcllogistics.com")
        print("  FLEETX_PASSWORD=his-fleetx-password\n")
        sys.exit(1)

    print(f"\nTCL Fleet Tracker — starting...")
    trucks, api_calls = asyncio.run(run_tracker(
        headless=args.headless,
        vehicle_filter=args.vehicle
    ))

    if args.json_output:
        print(json.dumps({"trucks": trucks, "api_endpoints": list(api_calls.keys())}, indent=2))
    else:
        print_report(trucks, api_calls, vehicle_filter=args.vehicle)


if __name__ == "__main__":
    main()
