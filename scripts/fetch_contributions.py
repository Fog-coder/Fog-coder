#!/usr/bin/env python3
"""Scrape public GitHub contribution data (no token) -> data/contributions.json.

Parses the contributions HTML fragment: each day is a <td data-date data-level>
and counts live in matching <tool-tip> elements.
"""
import json
import re
import datetime as dt
import requests
from bs4 import BeautifulSoup

USERNAME = "Fog-coder"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = "data/contributions.json"


def fetch_days():
    r = requests.get(URL, headers={"User-Agent": "profile-art/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # id -> count from tooltips ("No contributions" or "N contribution(s) on ...")
    counts = {}
    for tip in soup.select("tool-tip[for]"):
        text = tip.get_text(" ", strip=True)
        m = re.search(r"([\d,]+)\s+contribution", text)
        counts[tip["for"]] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for td in soup.select("td[data-date]"):
        date = td.get("data-date")
        if not date:
            continue
        level = int(td.get("data-level", 0) or 0)
        cid = td.get("id")
        count = counts.get(cid, 0)
        days.append({"date": date, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    cur = longest = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # current streak counts back from the most recent day
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
        else:
            break
    return cur, longest


def main():
    days = fetch_days()
    if not days:
        raise SystemExit("No contribution data parsed — page format may have changed.")

    total = sum(d["count"] for d in days)
    cur, longest = streaks(days)

    by_month = {}
    for d in days:
        key = d["date"][:7]
        by_month[key] = by_month.get(key, 0) + d["count"]

    data = {
        "username": USERNAME,
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "by_month": by_month,
        "days": days,
    }
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {OUT}: {len(days)} days, {total} contributions, "
          f"streak {cur} (longest {longest})")


if __name__ == "__main__":
    main()
