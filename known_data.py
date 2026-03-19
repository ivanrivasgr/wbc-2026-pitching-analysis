"""
wbc_2026_known_data.py
======================
ONLY real, citable data.

Every entry has a SOURCE tag.
If it doesn't have a source, it's not in here.

Sources used:
  A) MLB.com WBC 2026 pitching leaderboard — page 1 (25 entries sorted by IP)
     https://www.mlb.com/world-baseball-classic/stats/pitching/innings-pitched
     Observed: March 18, 2026

  B) ESPN game reports (semifinal VEN vs ITA, final VEN vs USA)
  C) CBS Sports final recap
  D) NBC Sports final recap
  E) Yahoo Sports — manager texts story
"""

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE A: MLB.com page 1 — top 25 pitchers by IP
# Columns: player, team, w, l, era, g, gs, ip, so, whip
# NOTE: This is only the top 25 by IP. The full leaderboard has ~300 entries.
#       We cannot make tournament-wide claims from this subset.
# ─────────────────────────────────────────────────────────────────────────────
PAGE1_RAW = [
    ("Logan Webb",         "USA",  2, 0,  1.04, 2, 2, "8.2", 11, 0.69),
    ("Ondrej Satoria",     "CZE",  0, 0,  0.00, 2, 1, "8.1",  6, 0.96),
    ("Javier Assad",       "MEX",  0, 1,  4.50, 2, 2, "8.0",  7, 1.13),
    ("Enzo Sawayama",      "BRA",  0, 0,  0.00, 2, 2, "8.0",  6, 0.75),
    ("Dylan DeLucia",      "ITA",  0, 0,  2.35, 2, 1, "7.2",  8, 0.65),
    ("Livan Moinelo",      "CUB",  1, 1,  0.00, 2, 2, "7.1",  8, 1.50),
    ("Eduardo Rivera",     "PUR",  0, 0,  4.05, 2, 1, "6.2",  9, 0.90),
    ("Jack O'Loughlin",    "AUS",  1, 0,  0.00, 2, 0, "6.1",  5, 0.79),
    ("Cristopher Sanchez", "DOM",  1, 0,  4.26, 2, 2, "6.1", 12, 1.58),
    ("Sam Aldegheri",      "ITA",  1, 0,  3.00, 2, 2, "6.0",  9, 1.00),
    ("Yariel Rodriguez",   "CUB",  0, 0,  1.50, 3, 0, "6.0", 10, 0.67),
    ("Alex Wells",         "AUS",  0, 0,  3.00, 2, 1, "6.0",  9, 0.83),
    ("Hyeong Jun So",      "KOR",  1, 0,  6.35, 3, 1, "5.2",  5, 1.59),
    ("Michael Soroka",     "CAN",  1, 1,  4.76, 2, 2, "5.2",  3, 1.94),
    ("Adrian Almeida",     "COL",  0, 1,  5.06, 2, 1, "5.1",  6, 0.75),
    ("Danilo Bermudez",    "NCA",  0, 1,  3.38, 2, 1, "5.1",  2, 0.38),
    ("Brayan Bello",       "DOM",  1, 0,  1.80, 1, 1, "5.0",  7, 0.20),
    ("Enmanuel De Jesus",  "VEN",  1, 0,  1.80, 1, 1, "5.0",  8, 0.40),
    ("Byeong Hyeon Jo",    "KOR",  0, 0,  1.80, 4, 0, "5.0",  4, 0.80),
    ("Ariel Jurado",       "PAN",  0, 0,  0.00, 1, 1, "5.0",  4, 0.60),
    ("Michal Kovala",      "CZE",  0, 1, 10.80, 2, 0, "5.0",  7, 1.40),
    ("Aaron Nola",         "ITA",  1, 0,  0.00, 1, 1, "5.0",  5, 1.00),
    ("Cal Quantrill",      "CAN",  1, 0,  0.00, 1, 1, "5.0",  5, 0.60),
    ("Erasmo Ramirez",     "NCA",  0, 0,  1.80, 1, 1, "5.0",  2, 1.20),
    ("Michael Lorenzen",   "ITA",  1, 0,  0.00, 1, 1, "4.2",  2, 0.64),
]

# ─────────────────────────────────────────────────────────────────────────────
# SOURCE B/C/D: Confirmed narrative facts from news reports
# These are facts — not modeled, not inferred.
# ─────────────────────────────────────────────────────────────────────────────
CONFIRMED_NARRATIVE = {
    "final_score":           "Venezuela 3, USA 2",
    "final_rodriguez_ip":    "4.1",    # CBS Sports
    "final_rodriguez_er":    2,        # CBS Sports (Harper HR)
    "final_rodriguez_pitch": 57,       # CBS Sports
    "pool_rodriguez_ip":     "2.2",    # NBC News
    "pool_rodriguez_er":     3,        # NBC News (vs Dominican Republic)
    "semi_montero_ip":       "1.1",    # ESPN
    "semi_montero_exit":     "injured",# ESPN
    "semi_bullpen_pitchers": 6,        # ESPN
    "semi_bullpen_ip":       "7.2",    # ESPN
    "semi_bullpen_er":       0,        # ESPN
    "mlb_texts_count":       3,        # ESPN / Yahoo — organizations texting López
    "tournament_record":     "6-1",    # CBS Sports
    "mvp":                   "Maikel García",  # Olympics.com
    "closer":                "Daniel Palencia",
    "source_final":          "CBS Sports / NBC Sports",
    "source_semi":           "ESPN",
    "source_texts":          "ESPN / Yahoo Sports",
}


def ip_to_float(s):
    parts = str(s).split(".")
    return round(int(parts[0]) + (int(parts[1]) if len(parts) > 1 else 0) / 3, 4)


def build_page1_df():
    """
    Returns DataFrame of the 25 MLB.com page-1 entries.
    SCOPE: Top 25 pitchers by IP only. Not tournament-complete.
    """
    rows = []
    for name, team, w, l, era, g, gs, ip, so, whip in PAGE1_RAW:
        ip_f = ip_to_float(ip)
        rows.append({
            "player":      name,
            "team":        team,
            "w": w, "l": l, "era": era,
            "g": g, "gs": gs,
            "relief_apps": g - gs,
            "role":        "Starter" if gs > 0 else "Reliever",
            "ip_display":  ip,
            "ip_decimal":  ip_f,
            "ip_per_gs":   round(ip_f / gs, 2) if gs > 0 else None,
            "so": so, "whip": whip,
            "source":      "MLB.com WBC 2026 stats page 1",
        })
    return pd.DataFrame(rows)


def get_page1_starters():
    df = build_page1_df()
    return df[df["gs"] > 0].copy()


def get_page1_starters_with_2gs():
    """
    Only starters with 2+ GS — these are the most representative of
    tournament-level starter usage since they faced the pitch limit multiple times.
    """
    df = build_page1_df()
    return df[(df["gs"] >= 2)].copy()


def get_venezuela_known():
    """
    Only the ONE Venezuela entry visible in page 1.
    Eduardo Rodriguez and Keider Montero are from news sources only —
    their stats come from CONFIRMED_NARRATIVE, not from the leaderboard.
    """
    df = build_page1_df()
    ven = df[df["team"] == "VEN"].copy()
    return ven


if __name__ == "__main__":
    df = build_page1_df()
    starters = get_page1_starters()
    starters_2gs = get_page1_starters_with_2gs()

    print("=== PAGE 1 DATASET (source: MLB.com) ===")
    print(f"Total entries:          {len(df)}")
    print(f"Starters (GS > 0):     {len(starters)}")
    print(f"Starters with 2+ GS:   {len(starters_2gs)}")

    print("\n=== STARTERS WITH 2+ GS — avg IP/start ===")
    print(f"Avg IP/start:  {starters_2gs['ip_per_gs'].mean():.2f}")
    print(f"Range:         {starters_2gs['ip_per_gs'].min():.2f} – {starters_2gs['ip_per_gs'].max():.2f}")
    print(starters_2gs[["player","team","gs","ip_per_gs"]].to_string(index=False))

    print("\n=== VENEZUELA (page 1) ===")
    print(get_venezuela_known()[["player","team","gs","ip_per_gs","era"]].to_string(index=False))

    print("\n=== CONFIRMED NARRATIVE FACTS ===")
    for k, v in CONFIRMED_NARRATIVE.items():
        print(f"  {k:30s}: {v}")
