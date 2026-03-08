#!/usr/bin/env python3
"""
Fetch Plex Watchlist RSS, choose 2 random movies, schedule them on 2 random days
this week at 8:30–10:30 PM (America/New_York), and export to an .ics file.

Usage:
  python3 plex_watchlist_to_ics.py --out plex_movies.ics

Optional:
  --count 2
  --start "20:30"
  --duration 120
  --week "this"  (or "next")
"""

import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

import requests


FEED_URL_DEFAULT = "https://rss.plex.tv/YOUR_WATCHLIST_ID"
TZID_DEFAULT = "America/New_York"


def parse_hhmm(s: str) -> tuple[int, int]:
    parts = s.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Time must be HH:MM (24-hour). Example: 20:30")
    h, m = int(parts[0]), int(parts[1])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("Invalid HH:MM time.")
    return h, m


def start_of_week_monday(dt: datetime) -> datetime:
    # Monday as start of week
    return dt - timedelta(days=dt.weekday())


def fetch_movies(feed_url: str) -> list[dict]:
    resp = requests.get(feed_url, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    movies = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        desc_el = item.find("description")
        link_el = item.find("link")

        title = title_el.text.strip() if title_el is not None and title_el.text else "Unknown"
        description = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        link = link_el.text.strip() if link_el is not None and link_el.text else ""

        movies.append({"title": title, "description": description, "link": link})

    return movies


def ics_escape(text: str) -> str:
    # Escape per iCalendar TEXT rules (minimal set)
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def format_dt_local(dt: datetime) -> str:
    # Local datetime format without timezone conversion (we’ll tag with TZID)
    return dt.strftime("%Y%m%dT%H%M%S")


def build_ics(events: list[dict], tzid: str) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PlexWatchlistToICS//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for ev in events:
        uid = ev.get("uid") or f"{uuid.uuid4()}@plex-watchlist"
        title = ics_escape(ev["title"])
        desc = ics_escape(ev.get("description", ""))
        link = ev.get("link", "").strip()
        if link:
            desc = (desc + "\\n\\n" if desc else "") + ics_escape(link)

        dtstart = format_dt_local(ev["start"])
        dtend = format_dt_local(ev["end"])

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc}",
            f"SUMMARY:{title}",
            f"DTSTART;TZID={tzid}:{dtstart}",
            f"DTEND;TZID={tzid}:{dtend}",
            f"DESCRIPTION:{desc}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    # iCalendar lines are CRLF-terminated
    return "\r\n".join(lines) + "\r\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default=FEED_URL_DEFAULT, help="Plex RSS watchlist feed URL")
    ap.add_argument("--out", default="plex_movies.ics", help="Output .ics file path")
    ap.add_argument("--count", type=int, default=2, help="How many movies to schedule")
    ap.add_argument("--start", default="20:30", help="Start time (HH:MM 24-hour)")
    ap.add_argument("--duration", type=int, default=120, help="Duration in minutes")
    ap.add_argument("--week", choices=["this", "next"], default="this", help="Schedule in this or next week")
    ap.add_argument("--seed", type=int, default=None, help="Optional random seed for repeatable output")
    ap.add_argument("--tzid", default=TZID_DEFAULT, help="TZID to write into the ICS (default America/New_York)")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    movies = fetch_movies(args.feed)
    if not movies:
        raise SystemExit("No items found in RSS feed.")

    count = max(1, min(args.count, len(movies)))
    selected = random.sample(movies, count)

    today = datetime.now()
    monday = start_of_week_monday(today)
    if args.week == "next":
        monday = monday + timedelta(days=7)

    # choose distinct days within the week
    day_indexes = sorted(random.sample(range(7), count))

    start_h, start_m = parse_hhmm(args.start)
    duration = timedelta(minutes=max(1, args.duration))

    events = []
    for i, movie in enumerate(selected):
        day = day_indexes[i]
        start_dt = (monday + timedelta(days=day)).replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end_dt = start_dt + duration

        events.append(
            {
                "title": f"🎬 {movie['title']}",
                "description": movie.get("description", ""),
                "link": movie.get("link", ""),
                "start": start_dt,
                "end": end_dt,
            }
        )

    ics_text = build_ics(events, args.tzid)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(ics_text)

    print(f"Wrote {len(events)} event(s) to: {args.out}")
    for ev in events:
        print(f" - {ev['title']} @ {ev['start'].strftime('%a %Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()