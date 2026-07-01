"""PAUL Group of Hotels — Property Intelligence Dashboard"""

import io
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="The PAUL Group of Hotels",
    layout="wide",
    page_icon="👑",
    initial_sidebar_state="collapsed",
)

# ── STYLES ────────────────────────────────────────────────────────────────────

st.html("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"] { font-family: 'Lato', sans-serif; background-color: #f5e6b8; }

  .pg-header {
    background: linear-gradient(180deg, #14192e 0%, #1e2744 100%);
    color: #f5e6b8; padding: 28px 36px 20px; margin-bottom: 24px;
    border-top: 4px solid #c9a84c; border-bottom: 4px solid #c9a84c; text-align: center;
  }
  .pg-crest { font-size: 13px; color: #c9a84c; letter-spacing: 10px; margin-bottom: 10px; }
  .pg-header h1 { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; margin: 0; letter-spacing: 3px; color: #f5e6b8; text-transform: uppercase; }
  .pg-rule { color: #c9a84c; font-size: 10px; letter-spacing: 4px; margin: 10px 0 8px; }
  .pg-header p { font-family: 'Playfair Display', serif; font-size: 11px; margin: 0; color: #c9a84c; letter-spacing: 2px; text-transform: uppercase; font-style: italic; }

  .section-hdr { font-family: 'Playfair Display', serif; font-size: 11px; font-weight: 700; color: #6b1c2a; text-transform: uppercase; letter-spacing: 2.5px; border-bottom: 2px double #c9a84c; padding-bottom: 6px; margin: 22px 0 12px; }
  .section-hdr::before { content: '◈  '; color: #c9a84c; }

  .prop-about { font-family: 'Lato', sans-serif; font-size: 14px; color: #2a1a0a; line-height: 1.7; background: #fdf5e0; border-left: 4px solid #c9a84c; padding: 14px 18px; border-radius: 0 6px 6px 0; margin-bottom: 16px; }

  [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif; color: #14192e; font-size: 24px !important; }
  [data-testid="stMetricLabel"] { font-family: 'Playfair Display', serif; color: #7a6040; text-transform: uppercase; font-size: 10px; letter-spacing: 1.2px; }

  [data-baseweb="tab-list"] { background: #14192e; border-radius: 4px; padding: 6px 8px; gap: 5px; flex-wrap: nowrap; overflow-x: auto; border: 1px solid #c9a84c; }
  [data-baseweb="tab"] { color: #9aaccf !important; font-family: 'Playfair Display', serif; font-size: 12px; letter-spacing: 1px; border-radius: 3px; padding: 10px 20px !important; white-space: nowrap; text-transform: uppercase; }
  [aria-selected="true"][data-baseweb="tab"] { background: #c9a84c !important; color: #14192e !important; font-weight: 700 !important; }

  [data-testid="stDataFrame"] { border: 1px solid #c9a84c; border-radius: 3px; }

  .ops-placeholder { background: #fdf5e0; border: 1px dashed #c9a84c; border-radius: 6px; padding: 32px; text-align: center; color: #8a7040; font-family: 'Playfair Display', serif; font-style: italic; margin-top: 8px; }

  .pg-footer { text-align:center; color:#7a6040; font-size:11px; margin-top:30px; padding:16px; border-top:2px double #c9a84c; letter-spacing:2px; font-family:'Playfair Display',serif; font-style:italic; }

  @media screen and (max-width: 768px) {
    .main .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 0.5rem !important; }
    .pg-header { padding: 16px; }
    .pg-header h1 { font-size: 18px; letter-spacing: 1.5px; }
    .pg-crest { letter-spacing: 5px; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    [data-baseweb="tab"] { font-size: 10px !important; padding: 8px 10px !important; }
  }
</style>
""")

# ── IMAGE HELPERS ─────────────────────────────────────────────────────────────

IMG_BASE = Path("assets/hotel-images")


def hotel_images(slug: str, limit: int = 8) -> list:
    d = IMG_BASE / slug
    if not d.exists():
        return []
    imgs = (
        sorted(d.glob("*.jpg"))
        + sorted(d.glob("*.jpeg"))
        + sorted(d.glob("*.png"))
    )
    return imgs[:limit]


def image_gallery(slug: str, cols: int = 3):
    imgs = hotel_images(slug)
    if not imgs:
        return
    st.markdown('<div class="section-hdr">Gallery</div>', unsafe_allow_html=True)
    grid = st.columns(cols)
    for i, p in enumerate(imgs):
        grid[i % cols].image(str(p), use_container_width=True)


# ── CWR MIS HELPERS ──────────────────────────────────────────────────────────

def _v(x):
    try:
        f = float(x)
        return 0.0 if f != f else f
    except (TypeError, ValueError):
        return 0.0


def _cr(val, d=2):
    v = _v(val)
    return "—" if v == 0 else f"₹{v/1e7:.{d}f} Cr"


def _pct_var(a, b):
    a, b = _v(a), _v(b)
    return (a - b) / abs(b) * 100 if b else None


CWR_LINE_ITEMS = [
    ("TOTAL REVENUE",            "total_rev",     "cr"),
    ("Room Revenue",             "room_rev",      "cr"),
    ("F&B Revenue",              "fb_rev",        "cr"),
    ("Nikaay (Spa)",             "nikaay_rev",    "cr"),
    ("Travel Desk",              "travel_desk",   "cr"),
    ("Curio Shop",               "curio",         "cr"),
    ("Activity & Others",        "activity",      "cr"),
    ("Total Payroll",            "total_payroll", "cr"),
    ("Other Expenses",           "other_exp",     "cr"),
    ("GOP",                      "gop",           "cr"),
    ("Fixed Expenses",           "fixed_exp",     "cr"),
    ("NOP before Tax",           "nop",           "cr"),
    ("Occupancy %",              "occ",           "pct"),
    ("Room Nights Sold",         "rns",           "int"),
    ("ARR",                      "arr",           "inr"),
    ("Segment — Direct",         "seg_direct",    "cr"),
    ("Segment — Travel Agent",   "seg_ta",        "cr"),
    ("Segment — MICE",           "seg_mice",      "cr"),
    ("Segment — OTA",            "seg_ota",       "cr"),
    ("Segment — Brand Website",  "seg_brand",     "cr"),
]
CWR_LINE_ITEM_NAMES = [x[0] for x in CWR_LINE_ITEMS]
CWR_LINE_ITEM_MAP   = {x[0]: (x[1], x[2]) for x in CWR_LINE_ITEMS}

CWR_MONTH_OPTIONS = [
    "Apr '25", "May '25", "Jun '25", "Jul '25", "Aug '25", "Sep '25",
    "Oct '25", "Nov '25", "Dec '25", "Jan '26", "Feb '26", "YTD",
]


def _fmt_val(val, fmt):
    v = _v(val)
    if fmt == "cr":
        return _cr(v)
    if fmt == "pct":
        return f"{v * 100:.1f}%" if v else "—"
    if fmt == "int":
        return f"{int(v):,}" if v else "—"
    if fmt == "inr":
        return f"₹{v:,.0f}" if v else "—"
    return str(v)


def _scale(series, fmt):
    if fmt == "cr":
        return [v / 1e7 for v in series]
    if fmt == "pct":
        return [v * 100 for v in series]
    return list(series)


def _y_label(fmt):
    return {"cr": "₹ Crores", "pct": "%", "inr": "₹", "int": ""}.get(fmt, "")


def _parse_cwr_mis(src):
    """Parse CWR MIS from a file path or Streamlit UploadedFile."""
    df = pd.read_excel(src, sheet_name="Consolidated", header=None)

    MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    ACT = [1,  4,  7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
    BUD = [2,  5,  8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
    LYC = [3,  6,  9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

    def r(i):
        row = df.iloc[i]
        return {
            "act": [_v(row.iloc[c]) for c in ACT],
            "bud": [_v(row.iloc[c]) for c in BUD],
            "ly":  [_v(row.iloc[c]) for c in LYC],
            "ya":  _v(row.iloc[37]),
            "yb":  _v(row.iloc[38]),
            "yl":  _v(row.iloc[39]),
        }

    return {
        "months":        MONTHS,
        "total_rev":     r(14),
        "room_rev":      r(2),
        "fb_rev":        r(3),
        "nikaay_rev":    r(4),
        "travel_desk":   r(5),
        "curio":         r(6),
        "activity":      r(8),
        "occ":           r(18),
        "rns":           r(19),
        "arr":           r(20),
        "room_goi":      r(25),
        "fb_goi":        r(83),
        "total_payroll": r(216),
        "other_exp":     r(229),
        "gop":           r(231),
        "fixed_exp":     r(242),
        "nop":           r(244),
        "seg_direct":    r(29),
        "seg_ta":        r(30),
        "seg_mice":      r(31),
        "seg_ota":       r(32),
        "seg_brand":     r(33),
    }


def load_cwr_mis():
    p = Path("assets/mis/cwr_mis.xlsx")
    return _parse_cwr_mis(p) if p.exists() else None


def render_cwr_mis_tab():
    mis = load_cwr_mis()

    if mis is None:
        st.markdown('<div class="section-hdr">Finance — MIS Report</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload CWR MIS Excel (needs the 'Consolidated' sheet)",
            type=["xlsx", "xls"],
            key="cwr_mis_upload",
        )
        if uploaded:
            try:
                mis = _parse_cwr_mis(uploaded)
            except Exception as e:
                st.error(f"Could not parse MIS file: {e}")
                return
        else:
            st.markdown("""<div class="ops-placeholder">
              <div style="font-size:36px;margin-bottom:10px;">📊</div>
              <div style="font-size:15px;font-weight:600;">Upload CWR MIS Report</div>
              <div style="font-size:12px;margin-top:8px;color:#a09070;">
                Drop the MIS Excel above — the full dashboard loads instantly.
              </div></div>""", unsafe_allow_html=True)
            return

    GOLD, NAVY, FOREST, MAROON = "#c9a84c", "#14192e", "#2d5a3d", "#8b4513"

    months_lbl = [
        f"{m} '25" if m in ("Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec") else f"{m} '26"
        for m in mis["months"]
    ]

    # ── YTD HEADLINE KPIs ─────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">FY 2025–26 &nbsp;·&nbsp; YTD Performance (Apr 2025 – Feb 2026)</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    tr = mis["total_rev"]
    tr_var = _pct_var(tr["ya"], tr["yb"])
    k1.metric("Total Revenue", _cr(tr["ya"]),
              delta=f"{tr_var:+.1f}% vs Budget" if tr_var is not None else None)

    g = mis["gop"]
    gop_margin = g["ya"] / tr["ya"] * 100 if tr["ya"] else 0
    g_var = _pct_var(g["ya"], g["yb"])
    k2.metric("GOP", _cr(g["ya"]),
              delta=f"{gop_margin:.1f}% margin · {g_var:+.1f}% vs Bud" if g_var is not None else f"{gop_margin:.1f}% margin",
              delta_color="off")

    occ = mis["occ"]
    occ_a = occ["ya"] * 100
    occ_b = occ["yb"] * 100
    occ_l = occ["yl"] * 100
    k3.metric("Occupancy %", f"{occ_a:.1f}%",
              delta=f"Bud {occ_b:.1f}% · LY {occ_l:.1f}%",
              delta_color="off")

    arr = mis["arr"]
    arr_var = _pct_var(arr["ya"], arr["yl"])
    k4.metric("ARR", f"₹{arr['ya']:,.0f}",
              delta=f"{arr_var:+.1f}% vs LY" if arr_var is not None else None)

    st.markdown("")

    # ── MONTHLY REVENUE TREND ─────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Monthly Revenue Trend</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_bar(name="Room Revenue", x=months_lbl,
                y=[v / 1e7 for v in mis["room_rev"]["act"]],
                marker_color=MAROON, opacity=0.85)
    fig.add_bar(name="F&B Revenue", x=months_lbl,
                y=[v / 1e7 for v in mis["fb_rev"]["act"]],
                marker_color=FOREST, opacity=0.85)
    fig.add_bar(name="Other Revenue", x=months_lbl,
                y=[(tr - rr - fb) / 1e7
                   for tr, rr, fb in zip(mis["total_rev"]["act"],
                                         mis["room_rev"]["act"],
                                         mis["fb_rev"]["act"])],
                marker_color="#9a8060", opacity=0.85)
    fig.add_scatter(name="Total Actual", x=months_lbl,
                    y=[v / 1e7 for v in mis["total_rev"]["act"]],
                    mode="lines+markers",
                    line=dict(color=GOLD, width=2.5), marker=dict(size=7, color=GOLD))
    fig.add_scatter(name="Budget", x=months_lbl,
                    y=[v / 1e7 for v in mis["total_rev"]["bud"]],
                    mode="lines", line=dict(color="#aaa", width=1.5, dash="dot"))
    fig.update_layout(
        barmode="stack",
        paper_bgcolor="#f5e6b8", plot_bgcolor="#fdf5e0",
        font=dict(family="Lato", color="#2a1a0a", size=12),
        yaxis_title="₹ Crores",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=30, b=10), height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── OCCUPANCY & ARR ───────────────────────────────────────────────────────
    c_occ, c_arr = st.columns(2)

    with c_occ:
        st.markdown('<div class="section-hdr">Occupancy % — Monthly</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_scatter(name="Actual", x=months_lbl,
                         y=[v * 100 for v in mis["occ"]["act"]],
                         mode="lines+markers", line=dict(color=GOLD, width=2.5),
                         marker=dict(size=6, color=GOLD))
        fig2.add_scatter(name="Budget", x=months_lbl,
                         y=[v * 100 for v in mis["occ"]["bud"]],
                         mode="lines", line=dict(color="#aaa", dash="dot", width=1.5))
        fig2.add_scatter(name="LY", x=months_lbl,
                         y=[v * 100 for v in mis["occ"]["ly"]],
                         mode="lines", line=dict(color=MAROON, dash="dash", width=1.5))
        fig2.update_layout(
            paper_bgcolor="#f5e6b8", plot_bgcolor="#fdf5e0",
            font=dict(family="Lato", color="#2a1a0a", size=11),
            yaxis_title="%", yaxis_range=[0, 100],
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10), height=260,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c_arr:
        st.markdown('<div class="section-hdr">ARR — Monthly</div>', unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_bar(name="Actual ARR", x=months_lbl,
                     y=mis["arr"]["act"], marker_color=GOLD, opacity=0.9)
        fig3.add_scatter(name="LY ARR", x=months_lbl, y=mis["arr"]["ly"],
                         mode="lines+markers",
                         line=dict(color=MAROON, dash="dash", width=1.5),
                         marker=dict(size=5, color=MAROON))
        fig3.update_layout(
            paper_bgcolor="#f5e6b8", plot_bgcolor="#fdf5e0",
            font=dict(family="Lato", color="#2a1a0a", size=11),
            yaxis_title="₹",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10), height=260,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── P&L SUMMARY ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">P&L Summary — YTD</div>', unsafe_allow_html=True)

    def pl_row(label, d, bold=False):
        pv = _pct_var(d["ya"], d["yb"])
        return {
            "Line Item":    label,
            "Actual":       _cr(d["ya"]),
            "Budget":       _cr(d["yb"]),
            "Last Year":    _cr(d["yl"]),
            "Var vs Bud":   f"{pv:+.1f}%" if pv is not None else "—",
        }

    pl_data = [
        pl_row("Room Revenue",     mis["room_rev"]),
        pl_row("F&B Revenue",      mis["fb_rev"]),
        pl_row("Nikaay (Spa)",     mis["nikaay_rev"]),
        pl_row("Travel Desk",      mis["travel_desk"]),
        pl_row("Activity & Others",mis["activity"]),
        pl_row("TOTAL REVENUE",    mis["total_rev"]),
        pl_row("Total Payroll",    mis["total_payroll"]),
        pl_row("Other Expenses",   mis["other_exp"]),
        pl_row("GOP",              mis["gop"]),
        pl_row("Fixed Expenses",   mis["fixed_exp"]),
        pl_row("NOP before Tax",   mis["nop"]),
    ]
    pl_df = pd.DataFrame(pl_data)

    def highlight_rows(row):
        bold_rows = {"TOTAL REVENUE", "GOP", "NOP before Tax"}
        base = "font-family: 'Lato', sans-serif; font-size: 13px;"
        if row["Line Item"] in bold_rows:
            return [base + "font-weight:700; background-color:#fdf0c8;"] * len(row)
        return [base] * len(row)

    st.dataframe(
        pl_df.style.apply(highlight_rows, axis=1),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    # ── MARKET SEGMENT MIX ────────────────────────────────────────────────────
    st.markdown("")
    st.markdown('<div class="section-hdr">Room Revenue — Market Segment Mix (YTD)</div>', unsafe_allow_html=True)

    seg_vals = {
        "Direct":        sum(mis["seg_direct"]["act"]),
        "Travel Agent":  sum(mis["seg_ta"]["act"]),
        "MICE":          sum(mis["seg_mice"]["act"]),
        "OTA":           sum(mis["seg_ota"]["act"]),
        "Brand Website": sum(mis["seg_brand"]["act"]),
    }
    seg_vals = {k: v for k, v in seg_vals.items() if v > 0}

    if seg_vals:
        fig4 = px.pie(
            names=list(seg_vals.keys()),
            values=list(seg_vals.values()),
            color_discrete_sequence=[NAVY, GOLD, MAROON, FOREST, "#6b1c2a"],
            hole=0.42,
        )
        fig4.update_traces(textposition="outside", textinfo="percent+label",
                           textfont_size=12)
        fig4.update_layout(
            paper_bgcolor="#f5e6b8",
            font=dict(family="Lato", color="#2a1a0a"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=340, showlegend=False,
        )
        col_pie, col_seg = st.columns([1.2, 1])
        col_pie.plotly_chart(fig4, use_container_width=True)

        seg_df = pd.DataFrame([
            {"Segment": k,
             "Revenue": _cr(v),
             "Mix %": f"{v / sum(seg_vals.values()) * 100:.1f}%"}
            for k, v in sorted(seg_vals.items(), key=lambda x: -x[1])
        ])
        with col_seg:
            st.markdown("")
            st.dataframe(seg_df, use_container_width=True, hide_index=True)

    # ── DRILL-DOWN ANALYSIS ───────────────────────────────────────────────────
    st.markdown("")
    st.markdown('<div class="section-hdr">Drill-Down Analysis</div>', unsafe_allow_html=True)

    dd1, dd2 = st.columns(2)
    with dd1:
        sel_item = st.selectbox("Line Item", CWR_LINE_ITEM_NAMES, key="dd_item_cwr")
    with dd2:
        sel_month = st.selectbox("Month", CWR_MONTH_OPTIONS,
                                 index=len(CWR_MONTH_OPTIONS) - 1, key="dd_month_cwr")

    data_key, fmt = CWR_LINE_ITEM_MAP[sel_item]
    data = mis[data_key]

    if sel_month == "YTD":
        act_val, bud_val, ly_val = data["ya"], data["yb"], data["yl"]
    else:
        mi = CWR_MONTH_OPTIONS.index(sel_month)
        act_val = data["act"][mi]
        bud_val = data["bud"][mi]
        ly_val  = data["ly"][mi]

    st.markdown("")
    m1, m2, m3 = st.columns(3)
    bud_delta = _pct_var(act_val, bud_val)
    ly_delta  = _pct_var(act_val, ly_val)
    m1.metric(f"Actual — {sel_month}",   _fmt_val(act_val, fmt))
    m2.metric(f"Budget — {sel_month}",   _fmt_val(bud_val, fmt),
              delta=f"{bud_delta:+.1f}% vs Budget" if bud_delta is not None else None)
    m3.metric(f"Last Year — {sel_month}", _fmt_val(ly_val, fmt),
              delta=f"{ly_delta:+.1f}% vs LY" if ly_delta is not None else None)

    st.markdown("")

    # Monthly trend for selected line item, highlight selected month
    mi_sel = None if sel_month == "YTD" else CWR_MONTH_OPTIONS.index(sel_month)
    bar_colors = [
        GOLD if (mi_sel is None or i == mi_sel) else "#ddc980"
        for i in range(12)
    ]

    act_y = _scale(data["act"], fmt)
    bud_y = _scale(data["bud"], fmt)
    ly_y  = _scale(data["ly"],  fmt)

    fig5 = go.Figure()
    fig5.add_bar(name="Actual", x=months_lbl, y=act_y,
                 marker_color=bar_colors, opacity=0.92)
    if any(v for v in bud_y):
        fig5.add_scatter(name="Budget", x=months_lbl, y=bud_y,
                         mode="lines+markers",
                         line=dict(color="#888", dash="dot", width=1.5),
                         marker=dict(size=5, color="#888"))
    if any(v for v in ly_y):
        fig5.add_scatter(name="Last Year", x=months_lbl, y=ly_y,
                         mode="lines+markers",
                         line=dict(color=MAROON, dash="dash", width=1.5),
                         marker=dict(size=5, color=MAROON))

    fig5.update_layout(
        title=dict(text=f"{sel_item} — Monthly Trend", font=dict(family="Playfair Display", size=14, color=NAVY)),
        paper_bgcolor="#f5e6b8", plot_bgcolor="#fdf5e0",
        font=dict(family="Lato", color="#2a1a0a", size=12),
        yaxis_title=_y_label(fmt),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
    )
    st.plotly_chart(fig5, use_container_width=True)


# ── PROPERTY DATA ─────────────────────────────────────────────────────────────

HOTELS = {
    "Kumarakom Lake Resort": {
        "slug": "kumarakom",
        "location": "Kumarakom, Kottayam, Kerala",
        "address": "Kumarakom North Post – Kottayam: 686 563, Kerala, India",
        "tel": "+91 481 2524900",
        "email": "reservationklr@thepaul.in",
        "website": "www.kumarakomlakeresort.in",
        "color": "#8b4513",
        "star": "5-Star Heritage",
        "about": "The five-star luxury heritage Kumarakom Lake Resort is set by the famed backwaters of Kumarakom, just 14 km from Kottayam in Central Kerala. Cochin International Airport is 72 km away. Bask in the pleasant touch of the warm cheery sun and the cool breeze amid Kerala's iconic backwaters.",
        "total_rooms": 72,
        "accommodation": [
            {"Category": "Luxury Pavilion Room",                        "sqft": 550,  "Inv": 12},
            {"Category": "Meandering Pool Villa",                       "sqft": 400,  "Inv": 25},
            {"Category": "Meandering Pool Duplex Villa",                "sqft": 600,  "Inv": 4},
            {"Category": "Heritage Villa with Private Pool",            "sqft": 450,  "Inv": 15},
            {"Category": "Heritage Lake View Villa with Private Pool",  "sqft": 450,  "Inv": 7},
            {"Category": "Presidential Suite with Private Pool",        "sqft": 1200, "Inv": 2},
            {"Category": "One Bedroom Houseboat",                       "sqft": "—",  "Inv": 2},
            {"Category": "One Bedroom Deluxe Houseboat",               "sqft": "—",  "Inv": 1},
            {"Category": "Two Bedroom Houseboat",                       "sqft": "—",  "Inv": 3},
            {"Category": "Four Bedroom Houseboat",                      "sqft": "—",  "Inv": 1},
        ],
        "dining": [
            {"Outlet": "Ettukettu",    "Cuisine": "Multi-cuisine",        "Covers": 116, "Timing": "07:30 am – 10:30 pm"},
            {"Outlet": "Vembanad",     "Cuisine": "Seafood Specialty",    "Covers": 56,  "Timing": "11:00 am – 10:30 pm"},
            {"Outlet": "Pool Pavilion","Cuisine": "Snacks & Drinks",      "Covers": 12,  "Timing": "11:00 am – 10:30 pm"},
            {"Outlet": "Thattukada",   "Cuisine": "Traditional Tea Shop", "Covers": 70,  "Timing": "4:00 pm – 5:30 pm"},
        ],
        "banquet": [
            {"Venue": "Conference Hall", "sqft": 1200,  "Dimensions": "62×20×12", "Theatre": "150", "Classroom": "110", "Cluster": "70"},
            {"Venue": "Houseboat",       "sqft": 1100,  "Dimensions": "68×16×7",  "Theatre": "80",  "Classroom": "42",  "Cluster": "36"},
            {"Venue": "Lake Side Lawns", "sqft": 10000, "Dimensions": "—",         "Theatre": "200", "Classroom": "—",   "Cluster": "—"},
            {"Venue": "Pool Side Lawns", "sqft": 3500,  "Dimensions": "—",         "Theatre": "75",  "Classroom": "—",   "Cluster": "—"},
        ],
        "spa": "Ayurmana — Green Leaf Certified Ayurveda Spa",
        "spa_treatments": ["Yoga & meditation", "Rejuvenation program", "Sirodhara", "Patrapodala swedam", "Choorna swedam", "Njavarakizhi", "Udwarthanam", "Pizhichil", "Ksheera sekam", "Weight reduction", "Panchakarma", "Anti-arthritic treatment", "Stress & anxiety treatment"],
        "services": ["24hr in-room dining", "Laundry/pressing", "24hr multilingual concierge", "Ayurveda center", "Airport transfers", "Non-smoking rooms", "Infinity swimming pool", "Daily sunset cruise", "Evening tea at Thattukada", "Evening cultural performances", "Valet parking"],
        "local_attractions": ["Backwater cruise", "Bird sanctuary", "Holy temples & churches", "Farm tours", "Kathakali", "Kalaripayattu", "Murals of Kerala", "Nature trails", "Travel to spice lands", "Smithery and pottery"],
        "onsite": ["Pottery", "Cane weaving", "Fishing", "Cultural programs", "Sunset cruise", "Speed boat", "Canoeing"],
        "special_events": [],
    },
    "The Paul Bangalore": {
        "slug": "paul-bangalore",
        "location": "Domlur, Bangalore, Karnataka",
        "address": "Opposite Embassy Golf Links, Off Intermediate Ring Road, Domlur Layout, Bangalore – 560071",
        "tel": "+91 80 4047 7777",
        "email": "reservationstpb@thepaul.in",
        "website": "www.thepaulbangalore.in",
        "color": "#6b1c2a",
        "star": "5-Star Boutique",
        "about": "The Paul Bangalore with its 58 suites is a luxury boutique hotel in India's IT hub. Strategically located opposite Embassy Golf Links — 35 km from Bangalore International Airport and 4 km from MG Road — redefining luxury through impeccable personal service.",
        "total_rooms": 58,
        "accommodation": [
            {"Category": "Studio Suite (One Bedroom)",    "sqft": 600,  "Inv": 20},
            {"Category": "Executive Suite (Two Bedroom)", "sqft": 800,  "Inv": 7},
            {"Category": "Premier Suite (Two Bedroom)",   "sqft": 1050, "Inv": 24},
            {"Category": "Club Suite (Two Bedroom)",      "sqft": 1200, "Inv": 7},
        ],
        "dining": [
            {"Outlet": "Sidewalk Café & Bar", "Cuisine": "Multi-cuisine",           "Covers": 72, "Timing": "07:00 am – 11:00 pm"},
            {"Outlet": "Vembanad",            "Cuisine": "Kerala & Coastal",         "Covers": 38, "Timing": "11:00 am–3:30 pm / 7:00 pm–11:00 pm"},
            {"Outlet": "Murphy's Brewhouse",  "Cuisine": "Irish Pub & Microbrewery", "Covers": 85, "Timing": "11:00 am–11:00 pm (1:00 am wknd)"},
            {"Outlet": "Masala Dani",         "Cuisine": "Mughlai & North Indian",   "Covers": 40, "Timing": "—"},
        ],
        "banquet": [
            {"Venue": "Conference Hall", "sqft": 2394, "Dimensions": "114×21×11", "Theatre": "180", "Classroom": "160", "Cluster": "120"},
            {"Venue": "Board Room I",    "sqft": 240,  "Dimensions": "20×12×9",   "Theatre": "12",  "Classroom": "—",   "Cluster": "—"},
            {"Venue": "Board Room II",   "sqft": 182,  "Dimensions": "14×13×9",   "Theatre": "7",   "Classroom": "—",   "Cluster": "—"},
        ],
        "spa": None,
        "spa_treatments": [],
        "services": ["24hr Business centre", "24hr Reception & Concierge", "24hr in-room dining", "In-house Travel Desk", "Free valet parking", "24hr Medical services on call", "Foreign currency exchange", "Conference/Meeting facilities", "Irish Pub & Microbrewery", "Wood-fired Italian Pizza Oven", "Indoor Swimming Pool", "Ultra-Modern gym", "Steam, Sauna & Jacuzzi", "Long stay amenities"],
        "local_attractions": ["MG Road (4 km)", "Embassy Golf Links", "Koramangala", "Indiranagar", "UB City"],
        "onsite": ["Steam", "Sauna", "Jacuzzi", "Indoor swimming pool", "Ultra-Modern gym"],
        "special_events": [],
    },
    "Forte Kochi": {
        "slug": "forte-kochi",
        "location": "Princess Street, Fort Kochi, Kerala",
        "address": "1/373, Princess Street, Fort Kochi, Kochi, Kerala 682001",
        "tel": "+91 484 270 4800",
        "email": "reservationfk@thepaul.in",
        "website": "www.fortekochi.in",
        "color": "#7a5c1e",
        "star": "Heritage Hotel",
        "about": "Gracefully tucked in the glories of the past, brimming with colonial charm and plush luxury, Forte Kochi is a captivating heritage hotel on the popular Princess Street in Fort Kochi. Built in the 1860's, the age-old Portuguese structure was once part of the palatial home of an eminent Jew family — a fascinating fusion of Portuguese, Dutch and British influences.",
        "total_rooms": 26,
        "accommodation": [
            {"Category": "Classic Room",           "sqft": 220, "Inv": 11},
            {"Category": "Imperial Room",          "sqft": 320, "Inv": 8},
            {"Category": "Imperial Superior Room", "sqft": 380, "Inv": 6},
            {"Category": "Sovereign Room",         "sqft": 420, "Inv": 1},
        ],
        "dining": [
            {"Outlet": "Jetty",         "Cuisine": "Multi-cuisine",             "Covers": 48, "Timing": "07:00 am–10:30 am / 12:30–3:30 pm / 7:00–10:30 pm"},
            {"Outlet": "Catch of Kochi","Cuisine": "Coastal",                   "Covers": 32, "Timing": "07:00 pm – 10:30 pm"},
            {"Outlet": "Thattukada",    "Cuisine": "Traditional Poolside Tea",  "Covers": 32, "Timing": "4:00 pm – 5:30 pm"},
        ],
        "banquet": [
            {"Venue": "—", "sqft": "—", "Dimensions": "—", "Theatre": "—", "Classroom": "—", "Cluster": "—"},
        ],
        "spa": "Ayurmana Spa",
        "spa_treatments": ["Abhayangam", "Sirodhara", "Patrapodala swedam", "Ayurveda facial", "Honey & Milk Facial", "Nalpalmaram Scrub Massage", "Head massage", "Face massage", "Feet massage", "Back massage", "Steam bath"],
        "services": ["24hr in-room dining", "Laundry/pressing", "24hr multilingual concierge", "Ayurveda spa", "Airport transfers", "Non-smoking rooms", "Bar", "Air-conditioned rooms", "Outdoor swimming pool", "Heritage walk tour", "Valet parking", "LED TV", "Mini bar", "Tea/Coffee maker", "Bathrobes"],
        "local_attractions": ["Kathakali Center", "Chinese Fishing Nets", "St. Francis Church", "Santa Cruz Basilica", "Mattanchery Palace", "Princess Street", "Jewish Synagogue", "Jew Street"],
        "onsite": ["Mikvah (ancient Jewish natural spring)", "Outdoor swimming pool"],
        "special_events": [],
    },
    "Coorg Wilderness Resort": {
        "slug": "coorg-wilderness",
        "location": "Mekeri, Madikeri, Coorg, Karnataka",
        "address": "Virajpet Main Road, Mekeri, Madikeri, Karnataka 571201",
        "tel": "+91-8272 226200 / +91 63646 01941",
        "email": "reservationcwr@thepaul.in",
        "website": "www.coorgwildernessresort.in",
        "color": "#2d5a3d",
        "star": "5-Star Eco-Luxury",
        "about": "At Coorg Wilderness Resort & Spa we bring you to the very doorstep of nature, offering a rare opportunity to be part of the wild, yet with every possible comfort and luxury. The ambience is so warm and the air so cool and cosy, air-conditioning is not required throughout the resort. Awaken to sweet birdsong and cool breezes.",
        "total_rooms": 104,
        "accommodation": [
            {"Category": "Wilderness Grove View Suite", "sqft": 870,  "Inv": 45},
            {"Category": "Wilderness Hill View Suite",  "sqft": 870,  "Inv": 7},
            {"Category": "Grand Grove View Suite",      "sqft": 1350, "Inv": 37},
            {"Category": "Grand Hill View Suite",       "sqft": 1350, "Inv": 15},
        ],
        "dining": [
            {"Outlet": "Habba",        "Cuisine": "Multi-cuisine",                    "Covers": 150, "Timing": "08:00–10:30 am / 01:00–3:30 pm / 7:30–10:30 pm"},
            {"Outlet": "Vembanad",     "Cuisine": "Coorg & Coastal Kerala Specialty", "Covers": 42,  "Timing": "12:00–3:00 pm / 7:00–10:30 pm"},
            {"Outlet": "Tipsy Bar",    "Cuisine": "Bar",                              "Covers": 36,  "Timing": "11:00 am – 10:30 pm"},
            {"Outlet": "Hunter Lounge","Cuisine": "Single Malt Whisky & Cigar",       "Covers": 32,  "Timing": "11:00 am – 10:30 pm"},
        ],
        "banquet": [
            {"Venue": "Grand Ball Room",       "sqft": 3500,          "Dimensions": "91×39×23",    "Theatre": "200", "Classroom": "150", "Cluster": "96"},
            {"Venue": "Queen's Court",         "sqft": 2000,          "Dimensions": "78×26×11-19", "Theatre": "60",  "Classroom": "35",  "Cluster": "48"},
            {"Venue": "Queen's Court Terrace", "sqft": "4200 (open)", "Dimensions": "95×44",        "Theatre": "—",   "Classroom": "—",   "Cluster": "—"},
        ],
        "spa": "Nikaay Spa",
        "spa_treatments": ["Body rituals", "Yoga rituals", "Face rituals", "Acupuncture", "Colonic irrigation", "Swedish therapy", "Aroma therapy", "Hot stone therapy", "Shirodhara", "Foot massage", "Back massage"],
        "services": ["24hr in-room dining", "Laundry/pressing", "24hr multilingual concierge", "World class spa", "Airport transfers", "Non-smoking rooms", "Infinity swimming pool", "Daily trek to sunset point", "Adventure activities", "Organic farm tour", "Nature walk", "Coffee experience center", "Valet parking"],
        "local_attractions": ["Coffee estate tours", "Buddhist monastery tour", "Tala Cauvery", "Tiger reserve tour", "Elephant camp tour"],
        "onsite": ["Adventure activities", "ATV rides", "Twitchers trek", "Walk to the sunset", "Coffee experience center", "Feeding the fish (4:30–5:00 pm)", "Organic farming & Animal Husbandry Tour", "Guided yoga sessions"],
        "special_events": [],
    },
    "Big Banyan Vineyard & Resort": {
        "slug": "big-banyan",
        "location": "Tavarakere, Bengaluru, Karnataka",
        "address": "No. 8/1, Chunchunkuppe, Tavarakere, Near Big Banyan Tree, Bengaluru – 562130",
        "tel": "+91 80 69111100",
        "email": "reservationstpb@thepaul.in",
        "website": "www.bigbanyanresort.in",
        "color": "#5c7a1c",
        "star": "Boutique Vineyard Resort",
        "about": "Set in 20 acres of sprawling greenery, Big Banyan Vineyard & Resort is just minutes from the famous Dodda Alada Mara — the 400-year-old banyan tree spanning 3 acres — and 30 km from Bangalore City. Our vineyards and winery offer the rare experience of witnessing the magical creation of exotic fine wines.",
        "total_rooms": 6,
        "accommodation": [
            {"Category": "Heritage Cottage",                        "sqft": 300, "Inv": 3},
            {"Category": "Ranch Residency (Two-bedroom apartment)", "sqft": 750, "Inv": 3},
        ],
        "dining": [
            {"Outlet": "Ranch", "Cuisine": "Multi-cuisine", "Covers": 195, "Timing": "07:00 am – 11:00 pm"},
        ],
        "banquet": [
            {"Venue": "Pool side Lawns", "sqft": 28000, "Dimensions": "200×140", "Theatre": "—", "Classroom": "—", "Cluster": "—"},
            {"Venue": "Ranch Lawns",     "sqft": 40000, "Dimensions": "260×160", "Theatre": "—", "Classroom": "—", "Cluster": "—"},
        ],
        "spa": None,
        "spa_treatments": [],
        "services": ["Wine tours & tasting", "Vineyard walk", "Organic farming", "Animal Husbandry", "Multi-cuisine restaurant", "Large event hosting", "Rain dance"],
        "local_attractions": ["Dodda Alada Mara (Big Banyan Tree)", "Bangalore city (30 km)", "Tavarakere village"],
        "onsite": ["Wine Tour", "Wine Tasting", "Virgin coconut oil pressing", "Rain dance", "Pickle ball court", "Organic Farming", "Animal Husbandry"],
        "special_events": ["Grape Harvest Festival", "Christmas Market", "New Year Celebrations", "Weekend Brunch"],
    },
}

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="pg-header">
  <div class="pg-crest">◆ &nbsp; ◆ &nbsp; ◆</div>
  <h1>The PAUL Group of Hotels</h1>
  <div class="pg-rule">── ✦ ──────────────────── ✦ ──</div>
  <p>Property Intelligence Dashboard &nbsp;·&nbsp; Powered by Vinya AI</p>
</div>
""", unsafe_allow_html=True)

# ── GROUP KPIs ────────────────────────────────────────────────────────────────

total_rooms  = sum(h["total_rooms"] for h in HOTELS.values())
total_dining = sum(len(h["dining"]) for h in HOTELS.values())
total_covers = sum(
    d["Covers"] for h in HOTELS.values()
    for d in h["dining"] if isinstance(d.get("Covers"), int)
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Properties", len(HOTELS))
k2.metric("Total Keys / Rooms", total_rooms)
k3.metric("F&B Outlets", total_dining)
k4.metric("Total Covers", total_covers)

st.markdown("")

# ── HOTEL TABS ────────────────────────────────────────────────────────────────

hotel_tabs = st.tabs(list(HOTELS.keys()))

for tab, (hotel_key, h) in zip(hotel_tabs, HOTELS.items()):
    with tab:
        color = h["color"]
        slug  = h["slug"]

        st.markdown(f"""
        <div style="border-left:4px solid {color}; padding:12px 18px; background:#fdf5e0;
                    margin-bottom:18px; border-radius:0 6px 6px 0;">
          <div style="font-family:'Playfair Display',serif; font-size:20px; color:{color}; font-weight:700;">{hotel_key}</div>
          <div style="font-size:12px; color:#7a6040; margin-top:3px;">{h['star']} &nbsp;·&nbsp; {h['location']}</div>
          <div style="font-size:11px; color:#9a8060; margin-top:3px;">
            ✆ {h['tel']} &nbsp;|&nbsp; ✉ {h['email']} &nbsp;|&nbsp; 🌐 {h['website']}
          </div>
        </div>
        """, unsafe_allow_html=True)

        view_tabs = st.tabs(["📋  Overview", "⚙️  Operations"])

        # ── OVERVIEW ──────────────────────────────────────────────────────────

        with view_tabs[0]:

            # Gallery — images extracted from hotel PDF
            image_gallery(slug, cols=3)

            st.markdown('<div class="section-hdr">About</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="prop-about">{h["about"]}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-hdr">At a Glance</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Keys", h["total_rooms"])
            c2.metric("Room Types", len(h["accommodation"]))
            c3.metric("Dining Outlets", len(h["dining"]))
            c4.metric("Banquet Venues", len(h["banquet"]))

            st.markdown("")

            col_acc, col_din = st.columns([1.3, 1])
            with col_acc:
                st.markdown('<div class="section-hdr">Accommodation</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(h["accommodation"]), use_container_width=True, hide_index=True)
            with col_din:
                st.markdown('<div class="section-hdr">Dining Outlets</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(h["dining"]), use_container_width=True, hide_index=True)

            st.markdown("")

            col_ban, col_svc = st.columns([1.4, 1])
            with col_ban:
                st.markdown('<div class="section-hdr">Banquet & Events</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(h["banquet"]), use_container_width=True, hide_index=True)
            with col_svc:
                st.markdown('<div class="section-hdr">Guest Services</div>', unsafe_allow_html=True)
                for svc in h["services"]:
                    st.markdown(f"· {svc}")

            st.markdown("")

            if h.get("spa"):
                st.markdown(f'<div class="section-hdr">{h["spa"]}</div>', unsafe_allow_html=True)
                spa_cols = st.columns(3)
                for i, t in enumerate(h["spa_treatments"]):
                    spa_cols[i % 3].markdown(f"· {t}")
                st.markdown("")

            col_local, col_onsite = st.columns(2)
            with col_local:
                st.markdown('<div class="section-hdr">Local Attractions</div>', unsafe_allow_html=True)
                for a in h["local_attractions"]:
                    st.markdown(f"· {a}")
            with col_onsite:
                st.markdown('<div class="section-hdr">On-site Experiences</div>', unsafe_allow_html=True)
                for o in h["onsite"]:
                    st.markdown(f"· {o}")

            if h.get("special_events"):
                st.markdown('<div class="section-hdr">Special Events</div>', unsafe_allow_html=True)
                ev_cols = st.columns(4)
                for i, ev in enumerate(h["special_events"]):
                    ev_cols[i % 4].markdown(f"🎉 {ev}")

        # ── OPERATIONS ────────────────────────────────────────────────────────

        with view_tabs[1]:

            ops_tabs = st.tabs(["💰 Finance", "📈 Sales", "🍽️ F&B", "📣 Content", "👥 HR"])

            with ops_tabs[0]:
                if hotel_key == "Coorg Wilderness Resort":
                    render_cwr_mis_tab()
                else:
                    st.markdown('<div class="section-hdr">Finance — MIS Report</div>', unsafe_allow_html=True)
                    uploaded = st.file_uploader(
                        f"Upload MIS Excel for {hotel_key}",
                        type=["xlsx", "xls"],
                        key=f"mis_{hotel_key}",
                    )
                    if uploaded:
                        try:
                            xl = pd.ExcelFile(uploaded)
                            sheets = xl.sheet_names
                            selected = (
                                st.selectbox("Sheet", sheets, key=f"sheet_{hotel_key}")
                                if len(sheets) > 1 else sheets[0]
                            )
                            df = pd.read_excel(uploaded, sheet_name=selected)
                            st.caption(f"{len(df)} rows · {len(df.columns)} columns · Sheet: {selected}")
                            st.dataframe(df, use_container_width=True, height=420)
                            buf = io.BytesIO()
                            df.to_excel(buf, index=False)
                            st.download_button("⬇ Download", buf.getvalue(),
                                               file_name=f"{hotel_key}_MIS.xlsx",
                                               mime="application/vnd.ms-excel",
                                               key=f"dl_{hotel_key}")
                        except Exception as e:
                            st.error(f"Could not read file: {e}")
                    else:
                        st.markdown(f"""<div class="ops-placeholder">
                          <div style="font-size:36px;margin-bottom:10px;">📊</div>
                          <div style="font-size:15px;font-weight:600;">Upload MIS Report</div>
                          <div style="font-size:12px;margin-top:8px;color:#a09070;">
                            Drop your Excel MIS sheet above to load financial data for {hotel_key}
                          </div></div>""", unsafe_allow_html=True)

            with ops_tabs[1]:
                st.markdown('<div class="section-hdr">Sales</div>', unsafe_allow_html=True)
                st.markdown("""<div class="ops-placeholder">
                  <div style="font-size:36px;margin-bottom:10px;">📈</div>
                  <div style="font-size:15px;font-weight:600;">Sales Data Coming Soon</div>
                  <div style="font-size:12px;margin-top:8px;">Connect your PMS or upload a sales report.</div>
                </div>""", unsafe_allow_html=True)

            with ops_tabs[2]:
                st.markdown('<div class="section-hdr">F&B — Outlet Summary</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(h["dining"]), use_container_width=True, hide_index=True)
                st.markdown("")
                fb1, fb2 = st.columns(2)
                fb1.metric("Total Outlets", len(h["dining"]))
                fb2.metric("Total Covers", sum(
                    d["Covers"] for d in h["dining"] if isinstance(d.get("Covers"), int)
                ))
                st.markdown("""<div class="ops-placeholder" style="margin-top:14px;">
                  <div style="font-size:12px;">Upload daily F&B report to track outlet-wise revenue.</div>
                </div>""", unsafe_allow_html=True)

            with ops_tabs[3]:
                st.markdown('<div class="section-hdr">Content</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="ops-placeholder">
                  <div style="font-size:36px;margin-bottom:10px;">📣</div>
                  <div style="font-size:15px;font-weight:600;">Content Calendar Coming Soon</div>
                  <div style="font-size:12px;margin-top:8px;">Social media and campaigns for {hotel_key}.</div>
                </div>""", unsafe_allow_html=True)

            with ops_tabs[4]:
                st.markdown('<div class="section-hdr">Human Resources</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="ops-placeholder">
                  <div style="font-size:36px;margin-bottom:10px;">👥</div>
                  <div style="font-size:15px;font-weight:600;">HR Data Coming Soon</div>
                  <div style="font-size:12px;margin-top:8px;">Team headcount and HR metrics for {hotel_key}.</div>
                </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.divider()
st.markdown('<div class="pg-footer">The PAUL Group of Hotels &nbsp;·&nbsp; Property Intelligence Dashboard &nbsp;·&nbsp; Built by Vinya AI</div>', unsafe_allow_html=True)
