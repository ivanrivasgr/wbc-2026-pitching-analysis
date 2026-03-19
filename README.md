# WBC 2026 · Pitch Limits & Pitching Strategy Analysis

**How pitch limits create a structural floor for bullpen usage in the World Baseball Classic**

📊 [Live Dashboard](https://wbc-2026-pitching-analysis-ahacejm2apvzgwzpikmvib.streamlit.app) &nbsp;·&nbsp; 📝 [Medium Article](https://medium.com/@ivanfgruber/pitch-limits-create-a-structural-floor-for-bullpen-usage-in-the-wbc-0d96a8eff541)

---

## What this is

A structural analysis of how WBC 2026 pitch limits (65 / 80 / 95) reshape pitching strategy and roster construction in short tournaments. Inspired by Venezuela's 2026 championship run.

The analysis combines three clearly separated layers:
- **Structural model** — arithmetic derived from official WBC rules + MLB benchmarks
- **Observed data** — MLB.com WBC 2026 leaderboard (top 25 by IP, partial sample)
- **Confirmed facts** — game statistics from named news outlets (ESPN, CBS, NBC, Yahoo)

No claim mixes these categories without labeling.

---

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Data sources

| Type | What | Source |
|---|---|---|
| Official rules | Pitch limits: 65 / 80 / 95 | WBC 2026 official tournament rules |
| MLB benchmarks | ~16.5 P/IP, ~38.9% bullpen share | Baseball Savant / FanGraphs 2022–24 |
| Observed data | Top 25 pitchers by IP | MLB.com WBC 2026 leaderboard (page 1, partial) |
| Confirmed facts | Final score, game lines, manager quotes | ESPN · CBS Sports · NBC News · Yahoo Sports |

### What is NOT in this project
- Team-level bullpen share percentages (insufficient data)
- Tournament-wide averages (only top 25 by IP available)
- Any claim about specific games not confirmed by a named outlet

---

## Files

| File | What it is |
|---|---|
| `app.py` | Streamlit dashboard |
| `model.py` | Structural constraint model |
| `known_data.py` | Real data — all entries sourced |
| `medium_article_final.md` | Full published article |
| `linkedin_post_final.txt` | LinkedIn post |
| `requirements.txt` | Python dependencies |