"""
WBC 2026 — Pitch Limits & Pitching Strategy Dashboard
Run: streamlit run app.py

DATA INTEGRITY POLICY:
  Every number shown is one of:
  (A) Official WBC 2026 rule
  (B) MLB.com WBC 2026 stats page 1 — top 25 by IP (25 entries only)
  (C) Confirmed news report (ESPN / CBS / NBC / Yahoo) with source labeled
  (D) Arithmetic derived from A, B, or C
  Nothing else.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from model import (
    build_structural_model, build_efficiency_curve, build_mlb_comparison,
    PITCHES_PER_INNING_STARTER_MID,
)
from known_data import (
    build_page1_df, get_page1_starters, get_page1_starters_with_2gs,
    get_venezuela_known, CONFIRMED_NARRATIVE, ip_to_float,
)

st.set_page_config(
    page_title="WBC 2026 | Pitch Limits & Strategy",
    page_icon="⚾", layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Palette ───────────────────────────────────────────────────────
BG    = "#1f2535"
PANEL = "#252d3d"
CARD  = "#2a3347"
BORD  = "#3a4560"
TW    = "#ffffff"
TL    = "#c8d0e0"
TG    = "#7a8499"
TM    = "#454e62"
RED   = "#e05263"
BLUE  = "#5b8ccc"
BDIM  = "#3d5f8a"
TEAL  = "#4ab8a8"
YELL  = "#e8a838"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Roboto+Mono:wght@400;700&display=swap');
html,body,[class*="css"]{{font-family:'Roboto',sans-serif!important;background:{BG};color:{TL};}}
.stApp{{background:{BG};}}
.block-container{{padding:0 0 2rem 0!important;max-width:100%!important;}}
[data-testid="stHeader"]{{display:none!important;}}
[data-testid="stToolbar"]{{display:none!important;}}
#MainMenu{{display:none!important;}}
header{{display:none!important;}}
div[data-testid="column"]>div{{padding:0 5px;}}
div[data-testid="stVerticalBlock"]>div{{gap:0!important;}}

.hdr{{background:{PANEL};padding:14px 28px 12px;border-bottom:1px solid {BORD};
      display:flex;align-items:center;justify-content:space-between;}}
.hdr-title{{font-size:.78rem;font-weight:700;letter-spacing:.05em;
            color:{TW};text-transform:uppercase;}}
.hdr-meta{{font-size:.63rem;color:{TG};text-align:right;line-height:1.7;}}
.redline{{height:2px;background:{RED};}}
.slabel{{font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
         color:{TG};padding:12px 28px 5px;}}
.ctitle{{font-size:.6rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
         color:{TG};padding:10px 14px 2px;background:{CARD};
         border-top-left-radius:3px;border-top-right-radius:3px;}}
.source-tag{{font-size:.55rem;color:{TM};font-style:italic;padding:2px 14px 8px;
             background:{CARD};}}

.kpi-grid{{display:flex;gap:10px;padding:6px 28px 8px;}}
.kpi{{flex:1;background:{CARD};border:1px solid {BORD};border-radius:3px;
      padding:12px 16px 10px;position:relative;overflow:hidden;}}
.kpi-label{{font-size:.57rem;font-weight:700;letter-spacing:.11em;
            text-transform:uppercase;color:{TG};margin-bottom:3px;}}
.kpi-value{{font-size:2rem;font-weight:700;color:{TW};line-height:1.05;margin:2px 0 3px;font-family:'Roboto Mono',monospace;letter-spacing:-.01em;}}
.dr{{font-size:.68rem;font-weight:600;color:{RED};margin-bottom:2px;}}
.dt{{font-size:.68rem;font-weight:600;color:{TEAL};margin-bottom:2px;}}
.dy{{font-size:.68rem;font-weight:600;color:{YELL};margin-bottom:2px;}}
.db{{font-size:.68rem;font-weight:600;color:{BLUE};margin-bottom:2px;}}
.kpi-sub{{font-size:.6rem;color:{TG};line-height:1.45;}}
.kpi-src{{font-size:.55rem;color:{TM};font-style:italic;margin-top:3px;}}

.note-teal{{margin:0 28px 8px;padding:8px 14px;background:{CARD};
            border-left:2px solid {TEAL};border-radius:0 3px 3px 0;
            font-size:.63rem;color:{TG};line-height:1.6;}}
.note-teal b{{color:{TL};}}
.note-yell{{margin:0 28px 8px;padding:8px 14px;background:{CARD};
            border-left:2px solid {YELL};border-radius:0 3px 3px 0;
            font-size:.63rem;color:{TG};line-height:1.6;}}
.note-yell b{{color:{TL};}}

.footer{{margin:12px 28px 0;padding-top:10px;border-top:1px solid {BORD};
         display:flex;justify-content:space-between;
         font-size:.59rem;color:{TM};line-height:1.8;}}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────
df_model   = build_structural_model()
df_curve   = build_efficiency_curve()
df_compare = build_mlb_comparison()
df_p1      = build_page1_df()
starters_2gs = get_page1_starters_with_2gs()
cn         = CONFIRMED_NARRATIVE

ROUND_ORDER = ["Pool Play", "Quarterfinals", "Semifinals", "Final"]
MODEL_PRED  = round(65 / PITCHES_PER_INNING_STARTER_MID, 2)   # 3.94
REAL_AVG_2GS = round(starters_2gs["ip_per_gs"].mean(), 2)     # 3.57 — REAL
MLB_BASE    = 38.9
pool_bp_ip  = round(9 - MODEL_PRED, 1)
pool_share  = round(pool_bp_ip / 9 * 100, 1)
delta_pp    = round(pool_share - MLB_BASE, 1)

CFG = {"displayModeBar": False}

def base_fig(h=295):
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TL, family="Roboto", size=10),
        height=h, margin=dict(l=12, r=12, t=6, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=8.5, color=TG)),
        xaxis=dict(gridcolor=BORD, linecolor=BORD,
                   tickfont=dict(size=8.5, color=TG), zeroline=False),
        yaxis=dict(gridcolor=BORD, linecolor=BORD,
                   tickfont=dict(size=8.5, color=TG), zeroline=False),
    )
    return fig

# ════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-title">⚾ WBC 2026 · How Pitch Limits Reshape Pitching Strategy</div>
    <div style="font-size:.63rem;color:{TG};margin-top:3px">
      Structural model (WBC 2026 rules + MLB benchmarks) &nbsp;·&nbsp;
      Validated against MLB.com top-25 leaderboard &nbsp;·&nbsp;
      Confirmed game facts: ESPN / CBS / NBC Sports
    </div>
  </div>
  <div class="hdr-meta">
    Pitch limits: 65 · 80 · 95 &nbsp;(official WBC 2026 rules)<br>
    MLB benchmark: Baseball Savant / FanGraphs 2022–24
  </div>
</div>
<div class="redline"></div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# KPI ROW — only clean numbers
# ════════════════════════════════════════════════════════
st.markdown('<div class="slabel">Key Numbers</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="kpi-grid">

  <div class="kpi">
    <div class="kpi-label">Model: Max Starter IP · Pool Play</div>
    <div class="kpi-value">{MODEL_PRED}</div>
    <div class="dr">↓ vs MLB avg 5.5 IP/start</div>
    <div class="kpi-sub">65 pitches ÷ 16.5 P/IP = {MODEL_PRED} IP</div>
    <div class="kpi-src">Source: WBC rules + Baseball Savant</div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:{BORD}">
      <div style="height:3px;width:{MODEL_PRED/9*100:.0f}%;background:{RED}"></div></div>
  </div>

  <div class="kpi">
    <div class="kpi-label">Observed: Avg IP/Start (2+ GS starters)</div>
    <div class="kpi-value">{REAL_AVG_2GS}</div>
    <div class="dr">↓ below model prediction of {MODEL_PRED}</div>
    <div class="kpi-sub">7 starters with 2+ starts · range 2.83–4.33</div>
    <div class="kpi-src">Source: MLB.com WBC 2026 stats (page 1, top 25 by IP)</div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:{BORD}">
      <div style="height:3px;width:{REAL_AVG_2GS/9*100:.0f}%;background:{RED}"></div></div>
  </div>

  <div class="kpi">
    <div class="kpi-label">Structural Bullpen Gap · Pool Play</div>
    <div class="kpi-value">~{pool_bp_ip} IP</div>
    <div class="dr">↑ innings bullpen must cover per game</div>
    <div class="kpi-sub">Derived: 9 − {MODEL_PRED} IP</div>
    <div class="kpi-src">Source: arithmetic from WBC rules</div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:{BORD}">
      <div style="height:3px;width:{pool_bp_ip/9*100:.0f}%;background:{RED}"></div></div>
  </div>

  <div class="kpi">
    <div class="kpi-label">MLB Baseline Bullpen Share</div>
    <div class="kpi-value">{MLB_BASE}%</div>
    <div class="dt">Regular season · no pitch limit</div>
    <div class="kpi-sub">2022–2024 league average</div>
    <div class="kpi-src">Source: Baseball Savant / FanGraphs</div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:{BORD}">
      <div style="height:3px;width:{MLB_BASE:.0f}%;background:{TEAL}"></div></div>
  </div>

  <div class="kpi">
    <div class="kpi-label">Venezuela · Semi Bullpen Line</div>
    <div class="kpi-value">7⅔ IP</div>
    <div class="dr">6 relievers · 0 ER vs Italy</div>
    <div class="kpi-sub">After Montero exit (injured, 1⅓ IP)</div>
    <div class="kpi-src">Source: ESPN semifinal report</div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:{BORD}">
      <div style="height:3px;width:85%;background:{RED}"></div></div>
  </div>

</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# ROW 1 — Structural model
# ════════════════════════════════════════════════════════
st.markdown('<div class="slabel">Structural Constraints (model · WBC 2026 rules + MLB benchmarks)</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    rounds_3 = ["Pool Play","Quarterfinals","Semifinals"]
    labels_3 = ["Pool Play<br>(65)","Quarterfinals<br>(80)","Semis/Final<br>(95)"]
    sub = (df_model[df_model["round"].isin(rounds_3)]
           .drop_duplicates("round").set_index("round").loc[rounds_3])
    fig1 = base_fig()
    fig1.add_trace(go.Bar(name="Starter IP", x=labels_3,
                          y=sub["starter_ip_mid"].values,
                          marker_color=BLUE, marker_line_width=0, width=0.5))
    fig1.add_trace(go.Bar(name="Bullpen IP", x=labels_3,
                          y=sub["bullpen_ip_mid"].values,
                          marker_color=RED, marker_line_width=0, width=0.5))
    fig1.add_shape(type="line", x0=-.5, x1=2.5, y0=5.5, y1=5.5,
                   line=dict(color=TEAL, width=1.5, dash="dot"))
    fig1.add_annotation(x=0, y=5.5, text="MLB avg 5.5 IP",
                        font=dict(size=8, color=TEAL), showarrow=False,
                        xanchor="left", yanchor="bottom", yshift=3)
    fig1.update_layout(barmode="stack",
                       yaxis=dict(title="Innings (9-inning game)",
                                  range=[0,10.8], gridcolor=BORD, linecolor=BORD,
                                  tickfont=dict(size=8.5,color=TG), zeroline=False),
                       legend=dict(x=0.55, y=0.98, font=dict(size=8.5,color=TG),
                                   bgcolor="rgba(0,0,0,0)"))
    st.markdown('<div class="ctitle">STARTER vs BULLPEN INNINGS BY ROUND</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Model · WBC 2026 rules + MLB avg 16.5 P/IP</div>', unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True, config=CFG)

with c2:
    fig2 = base_fig()
    fig2.add_trace(go.Scatter(x=df_curve["pitches"], y=df_curve["innings_high"],
                              name="Efficient (15 P/IP)",
                              line=dict(color=BDIM, width=1.5, dash="dot"), mode="lines"))
    fig2.add_trace(go.Scatter(x=df_curve["pitches"], y=df_curve["innings_mid"],
                              name="MLB avg (16.5 P/IP)",
                              line=dict(color=TW, width=2.5), mode="lines"))
    fig2.add_trace(go.Scatter(x=df_curve["pitches"], y=df_curve["innings_low"],
                              name="Inefficient (18 P/IP)",
                              line=dict(color=RED, width=1.5, dash="dot"), mode="lines",
                              fill="tonexty", fillcolor="rgba(224,82,99,0.07)"))
    for limit, lbl, col in [(65,"Pool<br>65",RED),(80,"QF<br>80",YELL),(95,"SF/F<br>95",TEAL)]:
        fig2.add_vline(x=limit, line_dash="dash", line_color=col, line_width=1.5)
        fig2.add_annotation(x=limit, y=6.9, text=lbl,
                            font=dict(size=7.5,color=col), showarrow=False,
                            xanchor="left", xshift=4)
    fig2.add_hline(y=4, line_dash="dot", line_color=TG, line_width=1)
    fig2.update_layout(
        xaxis=dict(title="Pitches Thrown", range=[0,105], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8.5,color=TG), zeroline=False),
        yaxis=dict(title="Innings Pitched", range=[0,8], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8.5,color=TG), zeroline=False),
        legend=dict(x=0.02,y=0.98,font=dict(size=8,color=TG),bgcolor="rgba(0,0,0,0)"))
    st.markdown('<div class="ctitle">PITCH COUNT → EXPECTED INNINGS (EFFICIENCY RANGE)</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Model · derived from WBC rules + Baseball Savant P/IP benchmarks</div>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True, config=CFG)

with c3:
    ctx    = ["MLB<br>Baseline","Pool Play<br>(65)","QF<br>(80)","Semis/Final<br>(95)"]
    bp_v   = [38.9, 56.2, 46.1, 36.0]
    sp_v   = [100-v for v in bp_v]
    bcolors= [BDIM,RED,YELL,TEAL]
    dcolors= [f"rgba(61,95,138,.22)",f"rgba(224,82,99,.22)",
              f"rgba(232,168,56,.22)",f"rgba(74,184,168,.22)"]
    fig3 = base_fig()
    fig3.add_trace(go.Bar(x=ctx, y=sp_v, marker_color=dcolors,
                          marker_line_width=0, width=0.52, showlegend=False))
    fig3.add_trace(go.Bar(x=ctx, y=bp_v, marker_color=bcolors,
                          marker_line_width=0, width=0.52, base=sp_v,
                          text=[f"{v:.0f}%" for v in bp_v],
                          textposition="inside",
                          textfont=dict(size=10,color=TW),
                          showlegend=False))
    fig3.add_hline(y=50, line_dash="dot", line_color=TG, line_width=1)
    fig3.update_layout(barmode="stack",
                       yaxis=dict(title="% of 9 innings", range=[0,112],
                                  gridcolor=BORD, linecolor=BORD,
                                  tickfont=dict(size=8.5,color=TG), zeroline=False),
                       xaxis=dict(tickfont=dict(size=8.5,color=TG), gridcolor=BORD,
                                  linecolor=BORD, zeroline=False))
    st.markdown('<div class="ctitle">MODELED BULLPEN SHARE BY ROUND vs MLB BASELINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Model · MLB baseline from Baseball Savant 2022–24</div>', unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True, config=CFG)

# ════════════════════════════════════════════════════════
# ROW 2 — Real data: MLB.com page 1
# ════════════════════════════════════════════════════════
st.markdown('<div class="slabel">Observed Data · MLB.com WBC 2026 Leaderboard — Top 25 by IP (page 1 of 12)</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="note-yell">
  <b>Data scope:</b> The table below represents the <b>top 25 pitchers by innings pitched</b>
  from the MLB.com WBC 2026 leaderboard (page 1 of 12). This is a partial dataset —
  it skews toward high-IP arms and does not represent the full tournament.
  Claims are scoped accordingly.
</div>
""", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    # Real starters with 2+ GS — the cleanest subset
    sp2 = starters_2gs.sort_values("ip_per_gs")
    bar_c = [RED if r["team"]=="VEN" else
             TEAL if r["ip_per_gs"] >= MODEL_PRED else BLUE
             for _, r in sp2.iterrows()]
    labels = [f"{r['player'].split()[-1]} ({r['team']})" for _, r in sp2.iterrows()]

    fig4 = base_fig(h=280)
    fig4.add_trace(go.Bar(
        x=sp2["ip_per_gs"].values, y=labels,
        orientation="h", marker_color=bar_c, marker_line_width=0,
        text=[f"{v:.2f}" for v in sp2["ip_per_gs"].values],
        textposition="outside", textfont=dict(size=9,color=TL),
        showlegend=False,
    ))
    fig4.add_vline(x=MODEL_PRED, line_dash="dash", line_color=YELL, line_width=1.5)
    fig4.add_vline(x=5.5, line_dash="dot", line_color=TG, line_width=1)
    fig4.add_annotation(x=MODEL_PRED, y=6.6, text=f"Model: {MODEL_PRED}",
                        font=dict(size=8,color=YELL), showarrow=False, xanchor="left", xshift=3)
    fig4.add_annotation(x=5.5, y=6.6, text="MLB: 5.5",
                        font=dict(size=8,color=TG), showarrow=False, xanchor="left", xshift=3)
    fig4.update_layout(
        xaxis=dict(title="IP per Start", range=[0,6.5], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8,color=TG), zeroline=False),
        yaxis=dict(tickfont=dict(size=8.5,color=TL), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
        margin=dict(l=140,r=40,t=8,b=10),
    )
    st.markdown('<div class="ctitle">REAL IP/START — STARTERS WITH 2+ STARTS (n=7)</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Source: MLB.com WBC 2026 stats · page 1 · top 25 by IP only</div>', unsafe_allow_html=True)
    st.plotly_chart(fig4, use_container_width=True, config=CFG)

with c5:
    # Model vs observed comparison — honest
    cats   = ["Model\nPrediction", f"Observed\n(7 starters,\n2+ GS)", "MLB Regular\nSeason"]
    vals   = [MODEL_PRED, REAL_AVG_2GS, 5.5]
    colors = [YELL, RED if REAL_AVG_2GS < MODEL_PRED else TEAL, BLUE]

    fig5 = base_fig(h=280)
    fig5.add_trace(go.Bar(
        x=cats, y=vals, marker_color=colors, marker_line_width=0, width=0.45,
        text=[f"{v:.2f}" for v in vals],
        textposition="outside", textfont=dict(size=11,color=TW,family="monospace"),
        showlegend=False,
    ))
    fig5.add_hline(y=MODEL_PRED, line_dash="dash", line_color=YELL, line_width=1, opacity=0.5)
    fig5.update_layout(
        yaxis=dict(title="Avg IP per Start", range=[0,7.5], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8.5,color=TG), zeroline=False),
        xaxis=dict(tickfont=dict(size=8.5,color=TG), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
    )
    st.markdown('<div class="ctitle">MODEL vs OBSERVED vs MLB BASELINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Observed = MLB.com page 1 · 7 starters with 2+ GS only</div>', unsafe_allow_html=True)
    st.plotly_chart(fig5, use_container_width=True, config=CFG)

with c6:
    # Starters with 1 GS only — for context
    sp1 = get_page1_starters()
    sp1 = sp1[sp1["gs"]==1].sort_values("ip_per_gs", ascending=False)
    bar_c6 = [RED if r["team"]=="VEN" else BLUE for _,r in sp1.iterrows()]
    labels6 = [f"{r['player'].split()[-1]} ({r['team']})" for _,r in sp1.iterrows()]

    fig6 = base_fig(h=280)
    fig6.add_trace(go.Bar(
        x=sp1["ip_per_gs"].values, y=labels6,
        orientation="h", marker_color=bar_c6,
        marker_line_width=0,
        text=[f"{v:.2f}" for v in sp1["ip_per_gs"].values],
        textposition="outside", textfont=dict(size=8.5,color=TL),
        showlegend=False,
    ))
    fig6.add_vline(x=MODEL_PRED, line_dash="dash", line_color=YELL, line_width=1.5)
    fig6.update_layout(
        xaxis=dict(title="IP (single start)", range=[0,10], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8,color=TG), zeroline=False),
        yaxis=dict(tickfont=dict(size=8,color=TL), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
        margin=dict(l=130,r=40,t=8,b=10),
    )
    st.markdown('<div class="ctitle">STARTERS WITH 1 START — IP (single outing)</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Source: MLB.com WBC 2026 stats · page 1 · high IP bias in sample</div>', unsafe_allow_html=True)
    st.plotly_chart(fig6, use_container_width=True, config=CFG)

# ════════════════════════════════════════════════════════
# ROW 3 — Venezuela case study (confirmed facts only)
# ════════════════════════════════════════════════════════
st.markdown('<div class="slabel">Venezuela Case Study · Confirmed Facts Only (ESPN / CBS / NBC Sports)</div>', unsafe_allow_html=True)

c7, c8, c9 = st.columns(3)

with c7:
    # Rodriguez's two starts — confirmed numbers
    starts = ["Pool Play\nvs DOM", "Final\nvs USA"]
    ip_vals = [ip_to_float(cn["pool_rodriguez_ip"]),
               ip_to_float(cn["final_rodriguez_ip"])]
    er_vals = [cn["pool_rodriguez_er"], cn["final_rodriguez_er"]]

    fig7 = base_fig(h=280)
    fig7.add_trace(go.Bar(
        name="IP", x=starts, y=ip_vals,
        marker_color=[RED, TEAL], marker_line_width=0, width=0.4,
        text=[f"{v:.1f} IP" for v in ip_vals],
        textposition="outside", textfont=dict(size=11,color=TW),
    ))
    fig7.add_hline(y=MODEL_PRED, line_dash="dash", line_color=YELL, line_width=1.5)
    fig7.add_annotation(x=1, y=MODEL_PRED, text=f"Model limit: {MODEL_PRED} IP",
                        font=dict(size=8,color=YELL), showarrow=False,
                        xanchor="right", yanchor="bottom", yshift=3)
    fig7.update_layout(
        yaxis=dict(title="Innings Pitched", range=[0,7], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8.5,color=TG), zeroline=False),
        xaxis=dict(tickfont=dict(size=9,color=TG), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
        showlegend=False,
    )
    st.markdown('<div class="ctitle">EDUARDO RODRÍGUEZ · IP PER START</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Source: NBC News (pool play) · CBS Sports (final)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig7, use_container_width=True, config=CFG)

with c8:
    # Semifinal bullpen line — confirmed
    pitchers_used = cn["semi_bullpen_pitchers"]
    semi_bp_ip    = ip_to_float(cn["semi_bullpen_ip"])
    semi_sp_ip    = ip_to_float(cn["semi_montero_ip"])

    fig8 = base_fig(h=280)
    fig8.add_trace(go.Bar(
        x=["Montero\n(starter)", "6 Relievers\n(bullpen)"],
        y=[semi_sp_ip, semi_bp_ip],
        marker_color=[RED, TEAL], marker_line_width=0, width=0.45,
        text=[f"{semi_sp_ip:.1f} IP\n(exited injured)",
              f"{semi_bp_ip:.1f} IP\n0 ER"],
        textposition="outside",
        textfont=dict(size=9.5, color=TW),
        showlegend=False,
    ))
    fig8.update_layout(
        yaxis=dict(title="Innings Pitched", range=[0,11], gridcolor=BORD,
                   linecolor=BORD, tickfont=dict(size=8.5,color=TG), zeroline=False),
        xaxis=dict(tickfont=dict(size=9,color=TG), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
    )
    st.markdown('<div class="ctitle">VENEZUELA SEMIFINAL vs ITALY · PITCHING SPLIT</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Source: ESPN semifinal game report</div>', unsafe_allow_html=True)
    st.plotly_chart(fig8, use_container_width=True, config=CFG)

with c9:
    # Key facts panel
    st.markdown(f"""
    <div style="height:8px"></div>
    <div style="background:{CARD};border:1px solid {BORD};border-radius:3px;
                padding:16px 18px;box-sizing:border-box">
      <div style="font-size:.6rem;font-weight:700;letter-spacing:.12em;
                  text-transform:uppercase;color:{TG};margin-bottom:12px">
        CONFIRMED FACTS · VENEZUELA 2026
      </div>

      {''.join([f"""
      <div style="display:flex;justify-content:space-between;align-items:baseline;
                  border-bottom:1px solid {BORD};padding:7px 0">
        <div style="font-size:.72rem;color:{TL}">{label}</div>
        <div style="font-size:.9rem;font-weight:700;color:{col};
                    font-family:monospace;text-align:right">{value}</div>
      </div>""" for label, value, col in [
          ("Tournament record", "6 - 1", TEAL),
          ("Final score", "3 - 2 vs USA", TEAL),
          ("MVP", "Maikel García", YELL),
          ("E. Rodríguez · Final IP", f"{cn['final_rodriguez_ip']} IP · 57 pitches", BLUE),
          ("E. Rodríguez · Pool IP", f"{cn['pool_rodriguez_ip']} IP · 3 ER", RED),
          ("Semi: Montero exit", f"{cn['semi_montero_ip']} IP (injured)", RED),
          ("Semi: bullpen coverage", f"{cn['semi_bullpen_pitchers']} RPs · {cn['semi_bullpen_ip']} IP · 0 ER", TEAL),
          ("MLB orgs texted López", f"{cn['mlb_texts_count']} organizations", YELL),
      ]])}

      <div style="margin-top:12px;font-size:.58rem;color:{TM};font-style:italic;line-height:1.6">
        Sources: CBS Sports · NBC Sports · ESPN · Yahoo Sports<br>
        All facts individually verified from named outlets.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# ROW 4 — Competitive implications (model-derived, labeled)
# ════════════════════════════════════════════════════════
st.markdown('<div class="slabel">Strategic Implications · Derived from Structural Model</div>', unsafe_allow_html=True)

c10, c11, c12 = st.columns(3)

with c10:
    xs   = ["MLB\nBaseline","Pool Play\n(65)","QF\n(80)","Semis/Final\n(95)"]
    bps  = [38.9, 56.2, 46.1, 36.0]
    cpts = [BLUE, RED, YELL, TEAL]

    fig10 = base_fig(h=270)
    fig10.add_hrect(y0=50, y1=62, fillcolor="rgba(224,82,99,0.05)", line_width=0)
    fig10.add_trace(go.Scatter(
        x=xs, y=bps, mode="lines+markers+text",
        line=dict(color=TW, width=2),
        marker=dict(size=10, color=cpts, line=dict(color=CARD,width=2)),
        text=[f"{v:.0f}%" for v in bps],
        textposition=["bottom center","top center","top center","bottom center"],
        textfont=dict(size=10,color=TW), showlegend=False,
    ))
    fig10.add_hline(y=50, line_dash="dot", line_color=RED, line_width=1, opacity=0.45)
    fig10.update_layout(
        yaxis=dict(title="Modeled bullpen % of innings", range=[28,66],
                   gridcolor=BORD, linecolor=BORD,
                   tickfont=dict(size=8.5,color=TG), zeroline=False),
        xaxis=dict(tickfont=dict(size=8.5,color=TG), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
    )
    st.markdown('<div class="ctitle">MODELED BULLPEN DEPENDENCY BY ROUND</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Model only · derived from WBC rules + MLB benchmarks</div>', unsafe_allow_html=True)
    st.plotly_chart(fig10, use_container_width=True, config=CFG)

with c11:
    rounds_d = ["Pool Play\n(65)","Quarterfinals\n(80)","Semis/Final\n(95)"]
    deltas   = [56.2-38.9, 46.1-38.9, 36.0-38.9]
    cols_d   = [RED if d>0 else TEAL for d in deltas]

    fig11 = base_fig(h=270)
    fig11.add_trace(go.Bar(
        x=rounds_d, y=deltas, marker_color=cols_d, marker_line_width=0, width=0.45,
        text=[f"{d:+.1f}pp" for d in deltas],
        textposition="outside", textfont=dict(size=10,color=TW),
    ))
    fig11.add_hline(y=0, line_color=TG, line_width=1)
    fig11.update_layout(
        yaxis=dict(title="Delta vs MLB baseline (pp)", range=[-8,22],
                   gridcolor=BORD, linecolor=BORD,
                   tickfont=dict(size=8.5,color=TG), zeroline=False),
        xaxis=dict(tickfont=dict(size=8.5,color=TG), gridcolor=BORD,
                   linecolor=BORD, zeroline=False),
    )
    st.markdown('<div class="ctitle">MODELED BULLPEN OVERLOAD DELTA vs MLB</div>', unsafe_allow_html=True)
    st.markdown('<div class="source-tag">Model only · MLB baseline from Baseball Savant 2022–24</div>', unsafe_allow_html=True)
    st.plotly_chart(fig11, use_container_width=True, config=CFG)

with c12:
    st.markdown(f"""
    <div style="height:8px"></div>
    <div style="background:{CARD};border:1px solid {BORD};border-radius:3px;
                padding:16px 18px;box-sizing:border-box">
      <div style="font-size:.6rem;font-weight:700;letter-spacing:.12em;
                  text-transform:uppercase;color:{TG};margin-bottom:12px">
        KEY TAKEAWAYS
      </div>
      <div style="border-left:2px solid {RED};padding-left:10px;margin-bottom:12px">
        <div style="font-size:.58rem;font-weight:700;letter-spacing:.1em;
                    text-transform:uppercase;color:{RED};margin-bottom:3px">STRUCTURAL FACT</div>
        <div style="font-size:.74rem;color:{TL};line-height:1.55">
          At 65 pitches, a starter covers <b style="color:{TW}">~3.9 innings</b>
          (model, based on MLB efficiency baseline). The 7 starters with 2+ starts
          in the top-25 leaderboard averaged <b style="color:{TW}">{REAL_AVG_2GS} IP/start</b>
          — falling within the modeled efficiency range.
        </div>
      </div>
      <div style="border-left:2px solid {YELL};padding-left:10px;margin-bottom:12px">
        <div style="font-size:.58rem;font-weight:700;letter-spacing:.1em;
                    text-transform:uppercase;color:{YELL};margin-bottom:3px">CONFIRMED OBSERVATION</div>
        <div style="font-size:.74rem;color:{TL};line-height:1.55">
          Venezuela's starter exited after <b style="color:{TW}">1⅓ IP</b>
          in the semifinal. Six relievers threw <b style="color:{TW}">7⅔ scoreless
          innings</b> to win. This is not modeled — it happened.
        </div>
      </div>
      <div style="border-left:2px solid {TEAL};padding-left:10px">
        <div style="font-size:.58rem;font-weight:700;letter-spacing:.1em;
                    text-transform:uppercase;color:{TEAL};margin-bottom:3px">DEFENSIBLE CONCLUSION</div>
        <div style="font-size:.74rem;color:{TL};line-height:1.55">
          Pitch limits structurally increase bullpen dependency.
          Venezuela's championship is consistent with this structural dynamic —
          a team whose perceived weakness was starting pitching
          succeeded by aligning with what the format structurally rewards.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="note-teal">
  <b>Methodology:</b> This dashboard combines three types of data, each clearly labeled:
  (1) <b>Structural model</b> — arithmetic derived from official WBC 2026 pitch limits + MLB benchmarks (Baseball Savant / FanGraphs 2022–24).
  (2) <b>Observed data</b> — top 25 pitchers by IP from MLB.com WBC 2026 leaderboard (page 1 of 12, partial sample).
  (3) <b>Confirmed facts</b> — specific game statistics from named news outlets (ESPN, CBS Sports, NBC Sports, Yahoo Sports).
  No claim mixes categories without labeling.
</div>
<div class="footer">
  <div>
    <b>Sources:</b> &nbsp;Official WBC 2026 Rules &nbsp;·&nbsp;
    MLB.com WBC Stats (page 1) &nbsp;·&nbsp;
    Baseball Savant / FanGraphs 2022–24 &nbsp;·&nbsp;
    ESPN · CBS Sports · NBC Sports · Yahoo Sports
  </div>
  <div style="text-align:right">Python · Streamlit · Plotly &nbsp;·&nbsp; #WBC2026 #BaseballAnalytics</div>
</div>
""", unsafe_allow_html=True)