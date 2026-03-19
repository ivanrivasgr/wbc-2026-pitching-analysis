"""
WBC 2026 — Structural Pitching Constraints Model
================================================
All values derived from:
  - Official WBC 2026 pitch limits (65 / 80 / 95)
  - Empirical MLB averages (public, citable)

No game data. No team data. No outcomes.
100% derived from rules + historical MLB benchmarks.
"""

import pandas as pd
import numpy as np

# ── Official WBC 2026 Pitch Limits ────────────────────────────────────────────
# Source: Official WBC 2026 Rules
PITCH_LIMITS = {
    "Pool Play":      65,
    "Quarterfinals":  80,
    "Semifinals":     95,
    "Final":          95,
}

# ── MLB Empirical Benchmarks (2022–2024 average, Baseball Savant / FanGraphs) ─
# These are defensible public figures:
#   Avg pitches per inning (starter): ~16.5  (range 15–18)
#   Avg pitches per inning (reliever): ~15.0  (range 14–16)
#   Source: Baseball Savant aggregated pitching logs 2022-2024
PITCHES_PER_INNING_STARTER_LOW  = 15.0   # efficient starter
PITCHES_PER_INNING_STARTER_MID  = 16.5   # MLB average starter
PITCHES_PER_INNING_STARTER_HIGH = 18.0   # inefficient / high stress

GAME_INNINGS = 9  # standard game length


def starter_capacity(pitch_limit: int, pitches_per_inning: float) -> float:
    """Max innings a starter can cover under a pitch limit."""
    return pitch_limit / pitches_per_inning


def bullpen_requirement(starter_innings: float, game_innings: int = 9) -> float:
    """Innings the bullpen must cover to complete the game."""
    return max(0, game_innings - starter_innings)


def build_structural_model() -> pd.DataFrame:
    """
    Build the full structural constraint table.
    Returns a DataFrame with columns:
        round, pitch_limit,
        starter_ip_low, starter_ip_mid, starter_ip_high,
        bullpen_ip_low, bullpen_ip_mid, bullpen_ip_high,
        bullpen_share_low, bullpen_share_mid, bullpen_share_high
    """
    rows = []
    for round_name, limit in PITCH_LIMITS.items():
        s_low  = starter_capacity(limit, PITCHES_PER_INNING_STARTER_HIGH)  # worst case for starter
        s_mid  = starter_capacity(limit, PITCHES_PER_INNING_STARTER_MID)
        s_high = starter_capacity(limit, PITCHES_PER_INNING_STARTER_LOW)   # best case for starter

        rows.append({
            "round":              round_name,
            "pitch_limit":        limit,
            # Starter innings range
            "starter_ip_low":     round(s_low,  2),
            "starter_ip_mid":     round(s_mid,  2),
            "starter_ip_high":    round(s_high, 2),
            # Bullpen requirement (inverted)
            "bullpen_ip_low":     round(bullpen_requirement(s_high), 2),
            "bullpen_ip_mid":     round(bullpen_requirement(s_mid),  2),
            "bullpen_ip_high":    round(bullpen_requirement(s_low),  2),
            # Bullpen share %
            "bullpen_share_low":  round(bullpen_requirement(s_high) / GAME_INNINGS * 100, 1),
            "bullpen_share_mid":  round(bullpen_requirement(s_mid)  / GAME_INNINGS * 100, 1),
            "bullpen_share_high": round(bullpen_requirement(s_low)  / GAME_INNINGS * 100, 1),
        })

    return pd.DataFrame(rows)


def build_efficiency_curve() -> pd.DataFrame:
    """
    Pitch count → expected innings curve for a range of efficiencies.
    Used for Chart 3: the constraint visualization.
    """
    pitch_counts = range(1, 101)
    rows = []
    for pc in pitch_counts:
        rows.append({
            "pitches":       pc,
            "innings_low":   round(pc / PITCHES_PER_INNING_STARTER_HIGH, 2),
            "innings_mid":   round(pc / PITCHES_PER_INNING_STARTER_MID,  2),
            "innings_high":  round(pc / PITCHES_PER_INNING_STARTER_LOW,  2),
        })
    df = pd.DataFrame(rows)

    # Add the WBC limit markers
    df["in_pool_play"]    = df["pitches"] == 65
    df["in_quarterfinal"] = df["pitches"] == 80
    df["in_semifinal"]    = df["pitches"] == 95
    return df


def build_mlb_comparison() -> pd.DataFrame:
    """
    WBC structural constraints vs MLB regular season averages.
    MLB figures: Baseball Savant / FanGraphs 2022-2024 league averages.
    Clearly labeled as external benchmarks.
    """
    return pd.DataFrame([
        {
            "context":          "MLB Regular Season\n(2022–2024 avg)",
            "avg_starter_ip":   5.5,
            "avg_bullpen_ip":   3.5,
            "bullpen_share_pct": 38.9,
            "pitch_limit":      "None",
            "source":           "Baseball Savant / FanGraphs",
        },
        {
            "context":          "WBC Pool Play\n(65-pitch limit)",
            "avg_starter_ip":   round(starter_capacity(65, PITCHES_PER_INNING_STARTER_MID), 1),
            "avg_bullpen_ip":   round(bullpen_requirement(starter_capacity(65, PITCHES_PER_INNING_STARTER_MID)), 1),
            "bullpen_share_pct": round(bullpen_requirement(starter_capacity(65, PITCHES_PER_INNING_STARTER_MID)) / 9 * 100, 1),
            "pitch_limit":      65,
            "source":           "Derived from WBC 2026 rules",
        },
        {
            "context":          "WBC Quarterfinals\n(80-pitch limit)",
            "avg_starter_ip":   round(starter_capacity(80, PITCHES_PER_INNING_STARTER_MID), 1),
            "avg_bullpen_ip":   round(bullpen_requirement(starter_capacity(80, PITCHES_PER_INNING_STARTER_MID)), 1),
            "bullpen_share_pct": round(bullpen_requirement(starter_capacity(80, PITCHES_PER_INNING_STARTER_MID)) / 9 * 100, 1),
            "pitch_limit":      80,
            "source":           "Derived from WBC 2026 rules",
        },
        {
            "context":          "WBC Semis / Final\n(95-pitch limit)",
            "avg_starter_ip":   round(starter_capacity(95, PITCHES_PER_INNING_STARTER_MID), 1),
            "avg_bullpen_ip":   round(bullpen_requirement(starter_capacity(95, PITCHES_PER_INNING_STARTER_MID)), 1),
            "bullpen_share_pct": round(bullpen_requirement(starter_capacity(95, PITCHES_PER_INNING_STARTER_MID)) / 9 * 100, 1),
            "pitch_limit":      95,
            "source":           "Derived from WBC 2026 rules",
        },
    ])


if __name__ == "__main__":
    print("=== STRUCTURAL CONSTRAINT MODEL ===\n")
    df = build_structural_model()
    print(df[["round", "pitch_limit", "starter_ip_mid", "bullpen_ip_mid", "bullpen_share_mid"]].to_string(index=False))

    print("\n=== WBC vs MLB COMPARISON ===\n")
    cmp = build_mlb_comparison()
    print(cmp[["context", "avg_starter_ip", "avg_bullpen_ip", "bullpen_share_pct"]].to_string(index=False))

    print("\n=== EFFICIENCY CURVE (sample) ===\n")
    curve = build_efficiency_curve()
    # Show only the limit points
    for limit in [65, 80, 95]:
        row = curve[curve["pitches"] == limit].iloc[0]
        print(f"  {limit} pitches → {row['innings_low']:.1f}–{row['innings_high']:.1f} IP (range by efficiency)")
