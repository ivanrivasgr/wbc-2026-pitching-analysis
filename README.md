# WBC 2026 · Pitch Limits & Pitching Strategy Analysis

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Data Integrity: What is and isn't in this project

Every number in this project is one of three things:

### Type A — Official rules
- WBC 2026 pitch limits: 65 (pool play) / 80 (QF) / 95 (SF, Final)
- Source: Official WBC 2026 tournament rules

### Type B — Public MLB benchmarks
- MLB avg pitches per inning: ~16.5 (2022–2024)
- MLB avg bullpen share: ~38.9% of innings (2022–2024)
- MLB avg starter IP: ~5.5 per start (2022–2024)
- Source: Baseball Savant, FanGraphs pitching leaderboards

### Type C — MLB.com WBC 2026 leaderboard (page 1 only)
- Top 25 pitchers by innings pitched
- URL: https://www.mlb.com/world-baseball-classic/stats/pitching/innings-pitched
- Observed: March 18, 2026
- **Scope: partial sample. High-IP bias. Not tournament-complete.**
- Claims using this data are scoped to "top 25 by IP" or "starters with 2+ starts"

### Type D — Confirmed news facts
Each fact has a named source:
| Fact | Source |
|---|---|
| Venezuela 3, USA 2 (final score) | CBS Sports, NBC Sports |
| E. Rodríguez: 4⅓ IP, 57 pitches (final) | CBS Sports |
| E. Rodríguez: 2⅔ IP, 3 ER (vs DOM) | NBC News |
| Montero: 1⅓ IP, exited injured (semi) | ESPN |
| 6 relievers: 7⅔ IP, 0 ER (semi) | ESPN |
| 3 MLB orgs texted López | ESPN / Yahoo Sports |
| Venezuela 6-1 record | CBS Sports |
| Maikel García: tournament MVP | Olympics.com |

### What is NOT in this project
- Team-level bullpen share percentages (not enough data)
- Tournament-wide averages beyond page 1 sample
- Any claim about specific games not confirmed by named outlets

---

## Files
| File | What it is |
|---|---|
| `app.py` | Streamlit dashboard |
| `model.py` | Structural constraint model (Type A + B) |
| `known_data.py` | Real data module (Type C + D) with sources |
| `linkedin_post.txt` | Ready-to-post LinkedIn content |
| `medium_article.md` | Full Medium article |
| `requirements.txt` | Python dependencies |
