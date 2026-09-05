#!/usr/bin/env python3
"""Render a cached GitHub activity card. Uses gh's existing auth; no extra PAT."""
import json
import subprocess
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

QUERY = '''query { user(login: "anndev-69") {
  contributionsCollection {
    totalCommitContributions totalPullRequestContributions totalIssueContributions
    contributionCalendar { totalContributions weeks {
      contributionDays { date contributionCount contributionLevel }
    } }
  }
} }'''
COLORS = {"NONE": "#202d32", "FIRST_QUARTILE": "#315b48",
          "SECOND_QUARTILE": "#518563", "THIRD_QUARTILE": "#91ba78",
          "FOURTH_QUARTILE": "#dbedac"}


def render(payload, updated):
    if payload.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; preserving the existing asset")
    collection = payload["data"]["user"]["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="title desc">
<title id="title">A year of showing up</title>
<desc id="desc">GitHub contribution activity over the last year. Counts follow GitHub profile visibility settings.</desc>
<rect x="1" y="1" width="958" height="348" rx="22" fill="#101c20" stroke="#31443f"/>
<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">
<text x="32" y="38" fill="#c6d7c5" font-size="13" letter-spacing="3">THE LONG GAME</text>
<text x="32" y="73" fill="#f1f4e9" font-size="28" font-weight="650">A year of showing up.</text>''']
    metrics = [(calendar["totalContributions"], "Contributions"),
               (collection["totalCommitContributions"], "Commits"),
               (collection["totalPullRequestContributions"], "Pull requests"),
               (collection["totalIssueContributions"], "Issues")]
    for i, (value, label) in enumerate(metrics):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Invalid contribution count")
        x = 32 + i * 232
        parts.append(f'<text x="{x}" y="126" fill="#dbedac" font-size="34" font-weight="650">{value:,}</text><text x="{x}" y="149" fill="#aabdb8" font-size="14">{label}</text>')
    weeks = calendar["weeks"]
    if not 1 <= len(weeks) <= 54:
        raise ValueError("Unexpected calendar length")
    previous_month = None
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week["contributionDays"]):
            parsed = date.fromisoformat(day["date"])
            x = 32 + week_index * 16.8
            y = 189 + ((parsed.weekday() + 1) % 7) * 15
            if day_index == 0 and parsed.month != previous_month:
                parts.append(f'<text x="{x:.1f}" y="179" fill="#aabdb8" font-size="10">{parsed.strftime("%b")}</text>')
                previous_month = parsed.month
            label = escape(f'{day["date"]}: {day["contributionCount"]} contributions')
            color = COLORS[day["contributionLevel"]]
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="12" height="11" rx="2" fill="{color}"><title>{label}</title></rect>')
    parts.append(f'<text x="32" y="323" fill="#aabdb8" font-size="12">Updated {escape(updated)} UTC · Last 12 months · GitHub profile activity</text>')
    parts.append('<text x="771" y="323" fill="#aabdb8" font-size="11">Less</text>')
    for i, color in enumerate(COLORS.values()):
        parts.append(f'<rect x="{801+i*17}" y="313" width="12" height="12" rx="2" fill="{color}"/>')
    parts.append('<text x="892" y="323" fill="#aabdb8" font-size="11">More</text></g></svg>\n')
    return "\n".join(parts)


def main():
    # A failed request/parse exits before any write: the last good card remains visible.
    result = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"],
                            capture_output=True, text=True, check=True, timeout=60)
    svg = render(json.loads(result.stdout), datetime.now(timezone.utc).date().isoformat())
    target = Path(__file__).resolve().parents[1] / "assets" / "activity.svg"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(target)
    print(f"Updated {target.name} from GitHub GraphQL")


if __name__ == "__main__":
    main()
