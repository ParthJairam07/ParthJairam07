"""Fetch the public contribution calendar (no token) into data/contributions.json.

    python scripts/fetch_contributions.py
"""
import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "ParthJairam07")
URL = f"https://github.com/users/{USER}/contributions"
COUNT_RE = re.compile(r"^(\d[\d,]*) contributions? on")


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        label = tips.get(td.get("id"), "")
        m = COUNT_RE.match(label)
        days.append(
            {
                "date": td["data-date"],
                "count": int(m.group(1).replace(",", "")) if m else 0,
                "level": int(td.get("data-level", 0)),
            }
        )
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup may have changed")
    return days


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    tail = list(reversed(days))
    # Today may still be empty; don't break the streak for it.
    if tail and tail[0]["count"] == 0:
        tail = tail[1:]
    for d in tail:
        if d["count"] == 0:
            break
        current += 1
    return current, longest


def main() -> None:
    resp = requests.get(URL, timeout=30, headers={"User-Agent": "profile-readme-bot"})
    resp.raise_for_status()
    days = parse(resp.text)
    soup = BeautifulSoup(resp.text, "html.parser")
    h2 = soup.find(id="js-contribution-activity-description")
    m = re.search(r"([\d,]+)", h2.get_text()) if h2 else None
    total = int(m.group(1).replace(",", "")) if m else sum(d["count"] for d in days)

    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    data = {
        "user": USER,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in days if d["count"] > 0),
        "monthly": dict(sorted(monthly.items())),
        "days": days,
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "contributions.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"{USER}: {total} contributions, {len(days)} days, streak {current} (best {longest})")


if __name__ == "__main__":
    main()
