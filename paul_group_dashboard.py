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
  html, body, [class*="css"] { font-family: 'Lato', sans-serif; background-color: #FFFFFF !important; }
  .stApp, .stApp > div, section.main, section.main > div,
  [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"],
  [data-testid="block-container"], [data-testid="stVerticalBlock"],
  .stMainBlockContainer, .main .block-container {
    background-color: #FFFFFF !important;
  }

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

  .prop-about { font-family: 'Lato', sans-serif; font-size: 14px; color: #2a1a0a; line-height: 1.7; background: #F8F8F8; border-left: 4px solid #c9a84c; padding: 14px 18px; border-radius: 0 6px 6px 0; margin-bottom: 16px; }

  [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif; color: #14192e; font-size: 24px !important; }
  [data-testid="stMetricLabel"] { font-family: 'Playfair Display', serif; color: #7a6040; text-transform: uppercase; font-size: 10px; letter-spacing: 1.2px; }

  [data-baseweb="tab-list"] { background: #14192e; border-radius: 4px; padding: 6px 8px; gap: 5px; flex-wrap: nowrap; overflow-x: auto; border: 1px solid #c9a84c; }
  [data-baseweb="tab"] { color: #9aaccf !important; font-family: 'Playfair Display', serif; font-size: 12px; letter-spacing: 1px; border-radius: 3px; padding: 10px 20px !important; white-space: nowrap; text-transform: uppercase; }
  [aria-selected="true"][data-baseweb="tab"] { background: #c9a84c !important; color: #14192e !important; font-weight: 700 !important; }

  [data-testid="stDataFrame"] { border: 1px solid #c9a84c; border-radius: 3px; }

  .ops-placeholder { background: #F8F8F8; border: 1px dashed #c9a84c; border-radius: 6px; padding: 32px; text-align: center; color: #8a7040; font-family: 'Playfair Display', serif; font-style: italic; margin-top: 8px; }

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


# ── CWR MIS ──────────────────────────────────────────────────────────────────

GOLD   = "#c9a84c"
NAVY   = "#14192e"
FOREST = "#2d5a3d"
MAROON = "#8b4513"
WINE   = "#6b1c2a"
MUTED  = "#9a8060"
RED    = "#c0392b"
_BG    = "#FFFFFF"
_PBG   = "#FAFAFA"
_TXT   = "#2a1a0a"
_GREY  = "#aaaaaa"


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


def _fmt_val(val, fmt):
    v = _v(val)
    if fmt == "cr":  return _cr(v)
    if fmt == "pct": return f"{v*100:.1f}%" if v else "—"
    if fmt == "int": return f"{int(v):,}" if v else "—"
    if fmt == "inr": return f"₹{v:,.0f}" if v else "—"
    return str(v)


def _scale(series, fmt):
    if fmt == "cr":  return [v/1e7 for v in series]
    if fmt == "pct": return [v*100 for v in series]
    return list(series)


def _y_label(fmt):
    return {"cr": "₹ Crores", "pct": "%", "inr": "₹", "int": ""}.get(fmt, "")


def _hdr(text):
    st.markdown(f'<div class="section-hdr">{text}</div>', unsafe_allow_html=True)


def _lo(h=300):
    return dict(
        paper_bgcolor=_BG, plot_bgcolor=_PBG,
        font=dict(family="Lato", color=_TXT, size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=10, b=10),
        height=h,
    )


# ── Drill-down registry ───────────────────────────────────────────────────────

CWR_LINE_ITEMS = [
    ("TOTAL REVENUE",           "total_rev",        "cr"),
    ("Room Revenue",            "room_rev",         "cr"),
    ("F&B Revenue",             "fb_rev",           "cr"),
    ("Nikaay (Spa)",            "nikaay_rev",       "cr"),
    ("Travel Desk",             "travel_desk",      "cr"),
    ("Curio Shop",              "curio",            "cr"),
    ("Activity",                "activity",         "cr"),
    ("Total Payroll",           "total_payroll",    "cr"),
    ("Other Expenses",          "total_other_exp",  "cr"),
    ("GOP",                     "gop",              "cr"),
    ("Fixed Expenses",          "total_fixed_exp",  "cr"),
    ("NOP before Tax",          "nop",              "cr"),
    ("Occupancy %",             "occ",              "pct"),
    ("Room Nights Sold",        "rns",              "int"),
    ("ARR",                     "arr",              "inr"),
    ("Segment — Direct",        "seg_direct",       "cr"),
    ("Segment — Travel Agent",  "seg_ta",           "cr"),
    ("Segment — MICE",          "seg_mice",         "cr"),
    ("Segment — OTA",           "seg_ota",          "cr"),
    ("Segment — Brand Website", "seg_brand",        "cr"),
]
CWR_LINE_ITEM_NAMES = [x[0] for x in CWR_LINE_ITEMS]
CWR_LINE_ITEM_MAP   = {x[0]: (x[1], x[2]) for x in CWR_LINE_ITEMS}
CWR_MONTH_OPTIONS   = [
    "Apr '25","May '25","Jun '25","Jul '25","Aug '25","Sep '25",
    "Oct '25","Nov '25","Dec '25","Jan '26","Feb '26","YTD",
]


# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_cwr_mis(src):
    df = pd.read_excel(src, sheet_name="Consolidated", header=None)
    MONTHS = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"]
    ACT = [1, 4, 7,10,13,16,19,22,25,28,31,34]
    BUD = [2, 5, 8,11,14,17,20,23,26,29,32,35]
    LYC = [3, 6, 9,12,15,18,21,24,27,30,33,36]

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

    tr_acts = [_v(df.iloc[14].iloc[c]) for c in ACT]
    active  = sum(1 for v in tr_acts if v > 0)

    return {
        "months":           MONTHS,
        "active":           active,
        # Revenue lines
        "room_rev":         r(2),
        "fb_rev":           r(3),
        "nikaay_rev":       r(4),
        "travel_desk":      r(5),
        "curio":            r(6),
        "adv_sports":       r(7),
        "activity":         r(8),
        "laundry":          r(9),
        "coffee_exp":       r(10),
        "coffee_store":     r(11),
        "estate":           r(12),
        "other_depts":      r(13),
        "total_rev":        r(14),
        # Room metrics
        "occ":              r(18),
        "rns":              r(19),
        "arr":              r(20),
        "room_goi":         r(25),
        # Market segments
        "seg_direct":       r(29),
        "seg_ta":           r(30),
        "seg_mice":         r(31),
        "seg_ota":          r(32),
        "seg_brand":        r(33),
        # F&B outlets
        "habba_covers":     r(39),
        "habba_apc":        r(40),
        "habba_rev":        r(43),
        "vemb_covers":      r(46),
        "vemb_rev":         r(50),
        "banq_covers":      r(53),
        "banq_rev":         r(58),
        "rsvc_covers":      r(61),
        "rsvc_rev":         r(65),
        "tipsy_covers":     r(68),
        "tipsy_rev":        r(73),
        "fb_goi":           r(83),
        "fb_total_covers":  r(95),
        "fb_apc":           r(96),
        # F&B cost
        "food_cost_pct":    r(189),
        "bev_cost_pct":     r(193),
        "fb_cost_pct":      r(198),
        # Nikaay
        "nikaay_treats":    r(103),
        "nikaay_rev_per_treat": r(105),
        "nikaay_total_rev": r(108),
        "nikaay_goi":       r(112),
        # Travel Desk
        "td_cars":          r(116),
        "td_rev_per_car":   r(118),
        "td_goi":           r(127),
        # Activity
        "activity_goi":     r(182),
        # Payroll
        "pay_rooms":        r(202),
        "pay_fb":           r(203),
        "pay_nikaay":       r(204),
        "pay_td":           r(205),
        "pay_admin":        r(211),
        "pay_it":           r(212),
        "pay_pomec":        r(213),
        "pay_hr":           r(214),
        "total_payroll":    r(216),
        "payroll_pct":      r(217),   # already in %, not decimal
        # Other expenses
        "exp_sm":           r(222),
        "exp_admin":        r(223),
        "exp_it":           r(224),
        "exp_energy":       r(225),
        "energy_per_room":  r(226),
        "exp_pomec":        r(227),
        "exp_hr":           r(228),
        "total_other_exp":  r(229),
        # Bottom line
        "gop":              r(231),
        "fix_insurance":    r(235),
        "fix_prop_tax":     r(237),
        "fix_finance":      r(238),
        "fix_depr":         r(240),
        "total_fixed_exp":  r(242),
        "nop":              r(244),
    }


@st.cache_data(show_spinner="Parsing MIS…")
def _cached_parse(b: bytes) -> dict:
    return _parse_cwr_mis(io.BytesIO(b))


def load_cwr_mis():
    p = Path("assets/mis/cwr_mis.xlsx")
    return _parse_cwr_mis(p) if p.exists() else None


# ── Executive tab ─────────────────────────────────────────────────────────────

def _mis_exec(mis, lbl):
    tr = mis["total_rev"];  g  = mis["gop"];   n  = mis["nop"]
    occ= mis["occ"];        arr= mis["arr"];   rr = mis["room_rev"]
    fb = mis["fb_rev"];     tp = mis["total_payroll"]
    fe = mis["total_fixed_exp"]
    act = mis["active"]

    period = f"Apr '25 – {lbl[act-1]}" if act < 12 else "FY 2025-26"
    st.caption(f"Period: {period}  ·  {act} months of actuals  ·  All figures in ₹ Crores")

    k1,k2,k3,k4,k5 = st.columns(5)
    gop_m  = g["ya"]/tr["ya"]*100 if tr["ya"] else 0
    tr_var = _pct_var(tr["ya"], tr["yb"])
    k1.metric("Total Revenue", _cr(tr["ya"]),
              delta=f"{tr_var:+.1f}% vs Budget" if tr_var else None)
    k2.metric("GOP", _cr(g["ya"]),
              delta=f"{gop_m:.1f}% margin", delta_color="off")
    k3.metric("NOP before Tax", _cr(n["ya"]))
    k4.metric("Occupancy %", f"{occ['ya']*100:.1f}%",
              delta=f"LY {occ['yl']*100:.1f}%", delta_color="off")
    k5.metric("ARR", f"₹{arr['ya']:,.0f}")
    st.markdown("")

    _hdr("Monthly Revenue Trend")
    anc = [tr["act"][i]-rr["act"][i]-fb["act"][i] for i in range(12)]
    fig = go.Figure()
    fig.add_bar(name="Room",      x=lbl, y=[v/1e7 for v in rr["act"]],  marker_color=MAROON, opacity=.85)
    fig.add_bar(name="F&B",       x=lbl, y=[v/1e7 for v in fb["act"]],  marker_color=FOREST, opacity=.85)
    fig.add_bar(name="Ancillary", x=lbl, y=[v/1e7 for v in anc],        marker_color=MUTED,  opacity=.85)
    fig.add_scatter(name="Total Actual", x=lbl, y=[v/1e7 for v in tr["act"]],
                    mode="lines+markers", line=dict(color=GOLD, width=2.5), marker=dict(size=7))
    fig.add_scatter(name="Budget", x=lbl, y=[v/1e7 for v in tr["bud"]],
                    mode="lines", line=dict(color=_GREY, dash="dot", width=1.5))
    fig.update_layout(barmode="stack", yaxis_title="₹ Crores", **_lo(300))
    st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        _hdr("Revenue Mix — YTD")
        anc_total = max(0, tr["ya"]-rr["ya"]-fb["ya"]-mis["nikaay_rev"]["ya"]
                        -mis["travel_desk"]["ya"]-mis["activity"]["ya"])
        rv = {k:v for k,v in {
            "Room Revenue": rr["ya"], "F&B Revenue": fb["ya"],
            "Nikaay (Spa)": mis["nikaay_rev"]["ya"],
            "Travel Desk":  mis["travel_desk"]["ya"],
            "Activity":     mis["activity"]["ya"],
            "Other":        anc_total,
        }.items() if v > 0}
        fig2 = px.pie(names=list(rv.keys()), values=list(rv.values()), hole=0.42,
                      color_discrete_sequence=[NAVY,MAROON,FOREST,GOLD,WINE,MUTED])
        fig2.update_traces(textinfo="percent+label", textfont_size=10, textposition="outside")
        fig2.update_layout(paper_bgcolor=_BG, font=dict(family="Lato"),
                           margin=dict(l=10,r=10,t=10,b=10), height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        _hdr("P&L Waterfall — YTD (₹ Cr)")
        oper_costs = tr["ya"] - g["ya"]
        fig3 = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","total","relative","total"],
            x=["Revenue","Operating Costs","GOP","Fixed Expenses","NOP"],
            y=[tr["ya"]/1e7, -oper_costs/1e7, g["ya"]/1e7, -fe["ya"]/1e7, n["ya"]/1e7],
            connector=dict(line=dict(color=GOLD, width=1, dash="dot")),
            increasing=dict(marker_color=FOREST),
            decreasing=dict(marker_color=RED),
            totals=dict(marker_color=NAVY),
            texttemplate="%{y:.2f}", textposition="outside",
        ))
        fig3.update_layout(showlegend=False, yaxis_title="₹ Crores",
                           paper_bgcolor=_BG, plot_bgcolor=_PBG,
                           font=dict(family="Lato",color=_TXT,size=10),
                           margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig3, use_container_width=True)

    _hdr("Drill-Down — Any Line Item × Month")
    dd1,dd2 = st.columns(2)
    sel_item  = dd1.selectbox("Line Item", CWR_LINE_ITEM_NAMES, key="dd_item_cwr")
    sel_month = dd2.selectbox("Month", CWR_MONTH_OPTIONS,
                              index=len(CWR_MONTH_OPTIONS)-1, key="dd_month_cwr")
    dk, fmt   = CWR_LINE_ITEM_MAP[sel_item]
    data      = mis[dk]
    if sel_month == "YTD":
        av,bv,lv = data["ya"],data["yb"],data["yl"]
    else:
        mi = CWR_MONTH_OPTIONS.index(sel_month)
        av,bv,lv = data["act"][mi],data["bud"][mi],data["ly"][mi]
    m1,m2,m3 = st.columns(3)
    bd = _pct_var(av,bv);  ld = _pct_var(av,lv)
    m1.metric(f"Actual — {sel_month}",    _fmt_val(av,fmt))
    m2.metric(f"Budget — {sel_month}",    _fmt_val(bv,fmt),
              delta=f"{bd:+.1f}% vs Budget" if bd else None)
    m3.metric(f"Last Year — {sel_month}", _fmt_val(lv,fmt),
              delta=f"{ld:+.1f}% vs LY"    if ld else None)
    mi_sel = None if sel_month=="YTD" else CWR_MONTH_OPTIONS.index(sel_month)
    bar_c  = [GOLD if (mi_sel is None or i==mi_sel) else "#ddc980" for i in range(12)]
    ay,by_,ly_ = _scale(data["act"],fmt), _scale(data["bud"],fmt), _scale(data["ly"],fmt)
    fig5 = go.Figure()
    fig5.add_bar(name="Actual", x=lbl, y=ay, marker_color=bar_c, opacity=.92)
    if any(by_): fig5.add_scatter(name="Budget", x=lbl, y=by_, mode="lines+markers",
                                   line=dict(color=_GREY,dash="dot",width=1.5), marker=dict(size=5))
    if any(ly_): fig5.add_scatter(name="LY", x=lbl, y=ly_, mode="lines+markers",
                                   line=dict(color=MAROON,dash="dash",width=1.5), marker=dict(size=5))
    fig5.update_layout(
        title=dict(text=f"{sel_item} — Monthly",
                   font=dict(family="Playfair Display",size=13,color=NAVY)),
        yaxis_title=_y_label(fmt),
        **{k:v for k,v in _lo(300).items() if k!="margin"},
        margin=dict(l=10,r=10,t=45,b=10),
    )
    st.plotly_chart(fig5, use_container_width=True)


# ── Rooms tab ─────────────────────────────────────────────────────────────────

def _mis_rooms(mis, lbl):
    rr=mis["room_rev"]; occ=mis["occ"]; arr=mis["arr"]; rns=mis["rns"]

    k1,k2,k3,k4 = st.columns(4)
    rr_var = _pct_var(rr["ya"],rr["yb"])
    k1.metric("Room Revenue YTD",   _cr(rr["ya"]),
              delta=f"{rr_var:+.1f}% vs Budget" if rr_var else None)
    k2.metric("Occupancy % YTD",    f"{occ['ya']*100:.1f}%",
              delta=f"Bud {occ['yb']*100:.1f}% · LY {occ['yl']*100:.1f}%", delta_color="off")
    k3.metric("ARR YTD",            f"₹{arr['ya']:,.0f}",
              delta=f"{_pct_var(arr['ya'],arr['yl']):+.1f}% vs LY" if _pct_var(arr['ya'],arr['yl']) else None)
    k4.metric("Room Nights Sold",   f"{int(rns['ya']):,}")
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        _hdr("Occupancy % — Monthly")
        fig = go.Figure()
        fig.add_scatter(name="Actual", x=lbl, y=[v*100 for v in occ["act"]],
                        mode="lines+markers", line=dict(color=GOLD,width=2.5), marker=dict(size=6))
        fig.add_scatter(name="Budget", x=lbl, y=[v*100 for v in occ["bud"]],
                        mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig.add_scatter(name="LY",     x=lbl, y=[v*100 for v in occ["ly"]],
                        mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig.update_layout(yaxis_title="%", yaxis_range=[0,100], **_lo(270))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        _hdr("ARR — Monthly")
        fig2 = go.Figure()
        fig2.add_bar(name="Actual ARR", x=lbl, y=arr["act"], marker_color=GOLD, opacity=.9)
        fig2.add_scatter(name="Budget", x=lbl, y=arr["bud"],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig2.add_scatter(name="LY",     x=lbl, y=arr["ly"],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig2.update_layout(yaxis_title="₹", **_lo(270))
        st.plotly_chart(fig2, use_container_width=True)

    _hdr("Room Nights Sold — Monthly")
    fig3 = go.Figure()
    fig3.add_bar(name="Actual",  x=lbl, y=rns["act"], marker_color=NAVY, opacity=.85)
    fig3.add_scatter(name="Budget", x=lbl, y=rns["bud"],
                     mode="lines+markers", line=dict(color=_GREY,dash="dot",width=1.5), marker=dict(size=5))
    fig3.add_scatter(name="LY",  x=lbl, y=rns["ly"],
                     mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
    fig3.update_layout(yaxis_title="Nights", **_lo(260))
    st.plotly_chart(fig3, use_container_width=True)

    _hdr("Market Segment Mix")
    segs = {"Direct":mis["seg_direct"],"Travel Agent":mis["seg_ta"],
            "MICE":mis["seg_mice"],"OTA":mis["seg_ota"],"Brand Website":mis["seg_brand"]}
    seg_ytd = {k:v["ya"] for k,v in segs.items() if v["ya"]>0}
    c_pie,c_tbl = st.columns([1.3,1])
    with c_pie:
        fig4 = px.pie(names=list(seg_ytd.keys()), values=list(seg_ytd.values()), hole=0.42,
                      color_discrete_sequence=[NAVY,GOLD,MAROON,FOREST,WINE])
        fig4.update_traces(textinfo="percent+label", textfont_size=11, textposition="outside")
        fig4.update_layout(paper_bgcolor=_BG, font=dict(family="Lato"),
                           margin=dict(l=10,r=10,t=10,b=10), height=300, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    with c_tbl:
        tot = sum(seg_ytd.values()) or 1
        seg_df = pd.DataFrame([
            {"Segment":k, "Revenue (YTD)":_cr(v), "Mix %":f"{v/tot*100:.1f}%",
             "vs LY":f"{_pct_var(v,segs[k]['yl']):+.1f}%" if _pct_var(v,segs[k]['yl']) else "—"}
            for k,v in sorted(seg_ytd.items(),key=lambda x:-x[1])
        ])
        st.markdown("")
        st.dataframe(seg_df, use_container_width=True, hide_index=True)

    _hdr("Segment Revenue — Monthly (₹ Cr)")
    fig5 = go.Figure()
    for (name,d),col in zip(segs.items(),[NAVY,GOLD,MAROON,FOREST,WINE]):
        fig5.add_bar(name=name, x=lbl, y=[v/1e7 for v in d["act"]], marker_color=col, opacity=.85)
    fig5.update_layout(barmode="stack", yaxis_title="₹ Crores", **_lo(280))
    st.plotly_chart(fig5, use_container_width=True)


# ── F&B tab ───────────────────────────────────────────────────────────────────

def _mis_fb(mis, lbl):
    fb=mis["fb_rev"]; fb_goi=mis["fb_goi"]; fb_cov=mis["fb_total_covers"]; fb_apc=mis["fb_apc"]

    k1,k2,k3,k4 = st.columns(4)
    fb_var = _pct_var(fb["ya"],fb["yb"])
    k1.metric("F&B Revenue YTD",  _cr(fb["ya"]),
              delta=f"{fb_var:+.1f}% vs Budget" if fb_var else None)
    k2.metric("F&B GOI YTD",      _cr(fb_goi["ya"]))
    k3.metric("Total Covers YTD", f"{int(fb_cov['ya']):,}")
    k4.metric("F&B APC YTD",      f"₹{fb_apc['ya']:,.0f}")
    st.markdown("")

    _hdr("F&B Revenue — Outlet Breakdown — Monthly (₹ Cr)")
    outlets = [
        ("Habba",         mis["habba_rev"],  MAROON),
        ("Vembanad",      mis["vemb_rev"],   FOREST),
        ("Banquets",      mis["banq_rev"],   NAVY),
        ("Room Service",  mis["rsvc_rev"],   GOLD),
        ("Tipsy / Hunters", mis["tipsy_rev"],WINE),
    ]
    fig = go.Figure()
    for name,d,col in outlets:
        fig.add_bar(name=name, x=lbl, y=[v/1e7 for v in d["act"]], marker_color=col, opacity=.85)
    fig.add_scatter(name="F&B Total", x=lbl, y=[v/1e7 for v in fb["act"]],
                    mode="lines+markers", line=dict(color=GOLD,width=2), marker=dict(size=6))
    fig.update_layout(barmode="stack", yaxis_title="₹ Crores", **_lo(300))
    st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        _hdr("Covers — Monthly")
        cov_outlets = [("Habba",mis["habba_covers"],MAROON),("Vembanad",mis["vemb_covers"],FOREST),
                       ("Banquets",mis["banq_covers"],NAVY),("Room Service",mis["rsvc_covers"],GOLD),
                       ("Tipsy",mis["tipsy_covers"],WINE)]
        fig2 = go.Figure()
        for name,d,col in cov_outlets:
            fig2.add_bar(name=name, x=lbl, y=d["act"], marker_color=col, opacity=.85)
        fig2.update_layout(barmode="stack", yaxis_title="Covers", **_lo(270))
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        _hdr("F&B APC — Monthly")
        fig3 = go.Figure()
        fig3.add_bar(name="APC", x=lbl, y=fb_apc["act"], marker_color=GOLD, opacity=.9)
        fig3.add_scatter(name="Budget", x=lbl, y=fb_apc["bud"],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig3.add_scatter(name="LY", x=lbl, y=fb_apc["ly"],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig3.update_layout(yaxis_title="₹ / Cover", **_lo(270))
        st.plotly_chart(fig3, use_container_width=True)

    _hdr("F&B Cost % — Monthly")
    fig4 = go.Figure()
    fig4.add_scatter(name="Total F&B Cost %", x=lbl,
                     y=[v*100 for v in mis["fb_cost_pct"]["act"]],
                     mode="lines+markers", line=dict(color=RED,width=2.5), marker=dict(size=7))
    fig4.add_scatter(name="Food Cost %", x=lbl,
                     y=[v*100 for v in mis["food_cost_pct"]["act"]],
                     mode="lines+markers", line=dict(color=MAROON,dash="dash",width=1.5), marker=dict(size=5))
    fig4.add_scatter(name="Beverage Cost %", x=lbl,
                     y=[v*100 for v in mis["bev_cost_pct"]["act"]],
                     mode="lines+markers", line=dict(color=FOREST,dash="dot",width=1.5), marker=dict(size=5))
    fig4.update_layout(yaxis_title="%", **_lo(260))
    st.plotly_chart(fig4, use_container_width=True)

    _hdr("F&B Outlet Summary — YTD")
    rows = []
    for name,rev_d,cov_d in [
        ("Habba",        mis["habba_rev"],  mis["habba_covers"]),
        ("Vembanad",     mis["vemb_rev"],   mis["vemb_covers"]),
        ("Banquets",     mis["banq_rev"],   mis["banq_covers"]),
        ("Room Service", mis["rsvc_rev"],   mis["rsvc_covers"]),
        ("Tipsy/Hunters",mis["tipsy_rev"],  mis["tipsy_covers"]),
    ]:
        tot_cov = int(sum(cov_d["act"]))
        rows.append({"Outlet":name, "Revenue (YTD)":_cr(rev_d["ya"]),
                     "vs Budget":f"{_pct_var(rev_d['ya'],rev_d['yb']):+.1f}%" if _pct_var(rev_d['ya'],rev_d['yb']) else "—",
                     "Covers (YTD)":f"{tot_cov:,}",
                     "APC":f"₹{rev_d['ya']/tot_cov:,.0f}" if tot_cov else "—"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── Ancillary tab ─────────────────────────────────────────────────────────────

def _mis_ancillary(mis, lbl):
    coffee_ya = mis["coffee_exp"]["ya"] + mis["coffee_store"]["ya"]

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Nikaay (Spa)",   _cr(mis["nikaay_total_rev"]["ya"]))
    k2.metric("Travel Desk",    _cr(mis["travel_desk"]["ya"]))
    k3.metric("Activity",       _cr(mis["activity"]["ya"]))
    k4.metric("Coffee (Total)", _cr(coffee_ya))
    k5.metric("Curio Shop",     _cr(mis["curio"]["ya"]))
    st.markdown("")

    _hdr("Ancillary Revenue — Monthly (₹ Cr)")
    coffee_act = [mis["coffee_exp"]["act"][i]+mis["coffee_store"]["act"][i] for i in range(12)]
    fig = go.Figure()
    for name,vals,col in [
        ("Nikaay",       [v/1e7 for v in mis["nikaay_rev"]["act"]],  GOLD),
        ("Travel Desk",  [v/1e7 for v in mis["travel_desk"]["act"]], NAVY),
        ("Activity",     [v/1e7 for v in mis["activity"]["act"]],    FOREST),
        ("Coffee",       [v/1e7 for v in coffee_act],                MAROON),
        ("Curio Shop",   [v/1e7 for v in mis["curio"]["act"]],       WINE),
    ]:
        fig.add_bar(name=name, x=lbl, y=vals, marker_color=col, opacity=.85)
    fig.update_layout(barmode="group", yaxis_title="₹ Crores", **_lo(280))
    st.plotly_chart(fig, use_container_width=True)

    # ── Nikaay ────────────────────────────────────────────────────────────────
    _hdr("Nikaay — Spa Detail")
    n1,n2,n3 = st.columns(3)
    n1.metric("Revenue YTD",      _cr(mis["nikaay_total_rev"]["ya"]))
    n2.metric("Total Treatments", f"{int(sum(mis['nikaay_treats']['act'])):,}")
    n3.metric("Rev / Treatment",  f"₹{mis['nikaay_rev_per_treat']['ya']:,.0f}")

    nc1,nc2 = st.columns(2)
    with nc1:
        fig2 = go.Figure()
        fig2.add_bar(name="Revenue", x=lbl,
                     y=[v/1e7 for v in mis["nikaay_total_rev"]["act"]], marker_color=GOLD, opacity=.9)
        fig2.add_scatter(name="Budget", x=lbl, y=[v/1e7 for v in mis["nikaay_rev"]["bud"]],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig2.add_scatter(name="LY", x=lbl, y=[v/1e7 for v in mis["nikaay_rev"]["ly"]],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig2.update_layout(yaxis_title="₹ Crores",
                           **{k:v for k,v in _lo(240).items() if k!="margin"},
                           margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)
    with nc2:
        fig3 = go.Figure()
        fig3.add_bar(name="Treatments", x=lbl,
                     y=mis["nikaay_treats"]["act"], marker_color=FOREST, opacity=.85)
        fig3.add_scatter(name="Rev/Treatment", x=lbl,
                         y=mis["nikaay_rev_per_treat"]["act"],
                         mode="lines+markers", line=dict(color=GOLD,width=2), marker=dict(size=5),
                         yaxis="y2")
        fig3.update_layout(
            yaxis=dict(title="Treatments"),
            yaxis2=dict(title="₹ Rev/Treatment", overlaying="y", side="right"),
            paper_bgcolor=_BG, plot_bgcolor=_PBG,
            font=dict(family="Lato",color=_TXT,size=11),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
            margin=dict(l=10,r=60,t=10,b=10), height=240)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Travel Desk ───────────────────────────────────────────────────────────
    _hdr("Travel Desk — Detail")
    td1,td2 = st.columns(2)
    with td1:
        st.metric("Revenue YTD", _cr(mis["travel_desk"]["ya"]))
        fig4 = go.Figure()
        fig4.add_bar(name="Revenue", x=lbl, y=[v/1e7 for v in mis["travel_desk"]["act"]],
                     marker_color=NAVY, opacity=.9)
        fig4.add_scatter(name="Budget", x=lbl, y=[v/1e7 for v in mis["travel_desk"]["bud"]],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig4.add_scatter(name="LY", x=lbl, y=[v/1e7 for v in mis["travel_desk"]["ly"]],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig4.update_layout(yaxis_title="₹ Crores",
                           **{k:v for k,v in _lo(230).items() if k!="margin"},
                           margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig4, use_container_width=True)
    with td2:
        st.metric("Total Cars YTD", f"{int(sum(mis['td_cars']['act'])):,}")
        fig5 = go.Figure()
        fig5.add_bar(name="Cars", x=lbl, y=mis["td_cars"]["act"], marker_color=GOLD, opacity=.85)
        fig5.add_scatter(name="Rev/Car", x=lbl, y=mis["td_rev_per_car"]["act"],
                         mode="lines+markers", line=dict(color=NAVY,width=2), marker=dict(size=5),
                         yaxis="y2")
        fig5.update_layout(
            yaxis=dict(title="No. of Cars"),
            yaxis2=dict(title="₹ Rev/Car", overlaying="y", side="right"),
            paper_bgcolor=_BG, plot_bgcolor=_PBG,
            font=dict(family="Lato",color=_TXT,size=11),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
            margin=dict(l=10,r=60,t=10,b=10), height=230)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Activity ──────────────────────────────────────────────────────────────
    _hdr("Activity — Monthly Revenue")
    fig6 = go.Figure()
    fig6.add_bar(name="Activity", x=lbl, y=[v/1e7 for v in mis["activity"]["act"]],
                 marker_color=FOREST, opacity=.9)
    fig6.add_scatter(name="Budget", x=lbl, y=[v/1e7 for v in mis["activity"]["bud"]],
                     mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
    fig6.add_scatter(name="LY", x=lbl, y=[v/1e7 for v in mis["activity"]["ly"]],
                     mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
    fig6.update_layout(yaxis_title="₹ Crores", **_lo(240))
    st.plotly_chart(fig6, use_container_width=True)


# ── Costs tab ─────────────────────────────────────────────────────────────────

def _mis_costs(mis, lbl):
    tp=mis["total_payroll"]; oe=mis["total_other_exp"]; fe=mis["total_fixed_exp"]

    k1,k2,k3 = st.columns(3)
    tp_var = _pct_var(tp["ya"],tp["yb"])
    k1.metric("Total Payroll YTD",      _cr(tp["ya"]),
              delta=f"{tp_var:+.1f}% vs Budget" if tp_var else None, delta_color="inverse")
    k2.metric("Other Expenses YTD",     _cr(oe["ya"]))
    k3.metric("Fixed Expenses YTD",     _cr(fe["ya"]))
    st.markdown("")

    c1,c2 = st.columns(2)
    with c1:
        _hdr("Payroll by Department — YTD")
        pay = [("Rooms", mis["pay_rooms"]["ya"]),("F&B",mis["pay_fb"]["ya"]),
               ("Nikaay",mis["pay_nikaay"]["ya"]),("Travel Desk",mis["pay_td"]["ya"]),
               ("Admin",mis["pay_admin"]["ya"]),("IT",mis["pay_it"]["ya"]),
               ("POMEC",mis["pay_pomec"]["ya"]),("HR",mis["pay_hr"]["ya"])]
        pay_s = sorted(pay, key=lambda x:x[1])
        fig = go.Figure(go.Bar(
            x=[v/1e7 for _,v in pay_s], y=[n for n,_ in pay_s],
            orientation="h", marker_color=NAVY, opacity=.85,
            text=[_cr(v) for _,v in pay_s], textposition="outside",
        ))
        fig.update_layout(xaxis_title="₹ Crores",
                          paper_bgcolor=_BG, plot_bgcolor=_PBG,
                          font=dict(family="Lato",color=_TXT,size=11),
                          margin=dict(l=10,r=10,t=10,b=10), height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        _hdr("Payroll % to Revenue — Monthly")
        pct_r = mis["payroll_pct"]
        fig2 = go.Figure()
        fig2.add_scatter(name="Actual %", x=lbl, y=pct_r["act"],
                         mode="lines+markers", line=dict(color=RED,width=2.5), marker=dict(size=7))
        fig2.add_scatter(name="Budget", x=lbl, y=pct_r["bud"],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig2.add_scatter(name="LY", x=lbl, y=pct_r["ly"],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig2.update_layout(yaxis_title="%", **_lo(300))
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        _hdr("Other Expenses — YTD Breakdown")
        exp = {"Sales & Marketing":mis["exp_sm"]["ya"],"Administration":mis["exp_admin"]["ya"],
               "IT":mis["exp_it"]["ya"],"Energy":mis["exp_energy"]["ya"],
               "POMEC":mis["exp_pomec"]["ya"],"HR":mis["exp_hr"]["ya"]}
        exp_s = sorted(exp.items(), key=lambda x:x[1])
        fig3 = go.Figure(go.Bar(
            x=[v/1e7 for _,v in exp_s], y=[k for k,_ in exp_s],
            orientation="h", marker_color=MAROON, opacity=.85,
            text=[_cr(v) for _,v in exp_s], textposition="outside",
        ))
        fig3.update_layout(xaxis_title="₹ Crores",
                           paper_bgcolor=_BG, plot_bgcolor=_PBG,
                           font=dict(family="Lato",color=_TXT,size=11),
                           margin=dict(l=10,r=10,t=10,b=10), height=280, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        _hdr("Energy Cost per Occupied Room — Monthly")
        fig4 = go.Figure()
        fig4.add_bar(name="Actual", x=lbl, y=mis["energy_per_room"]["act"],
                     marker_color=GOLD, opacity=.9)
        fig4.add_scatter(name="Budget", x=lbl, y=mis["energy_per_room"]["bud"],
                         mode="lines", line=dict(color=_GREY,dash="dot",width=1.5))
        fig4.add_scatter(name="LY", x=lbl, y=mis["energy_per_room"]["ly"],
                         mode="lines", line=dict(color=MAROON,dash="dash",width=1.5))
        fig4.update_layout(yaxis_title="₹ / Occupied Room", **_lo(280))
        st.plotly_chart(fig4, use_container_width=True)

    _hdr("Fixed Expenses — YTD")
    fix_df = pd.DataFrame([
        {"Item":"Finance Cost",   "Actual":_cr(mis["fix_finance"]["ya"]),
         "Budget":_cr(mis["fix_finance"]["yb"]),   "LY":_cr(mis["fix_finance"]["yl"])},
        {"Item":"Depreciation",   "Actual":_cr(mis["fix_depr"]["ya"]),
         "Budget":_cr(mis["fix_depr"]["yb"]),      "LY":_cr(mis["fix_depr"]["yl"])},
        {"Item":"Property Tax",   "Actual":_cr(mis["fix_prop_tax"]["ya"]),
         "Budget":_cr(mis["fix_prop_tax"]["yb"]),  "LY":_cr(mis["fix_prop_tax"]["yl"])},
        {"Item":"Insurance",      "Actual":_cr(mis["fix_insurance"]["ya"]),
         "Budget":_cr(mis["fix_insurance"]["yb"]), "LY":_cr(mis["fix_insurance"]["yl"])},
        {"Item":"TOTAL FIXED",    "Actual":_cr(mis["total_fixed_exp"]["ya"]),
         "Budget":_cr(mis["total_fixed_exp"]["yb"]),"LY":_cr(mis["total_fixed_exp"]["yl"])},
    ])
    st.dataframe(fix_df, use_container_width=True, hide_index=True)


# ── Full P&L tab ──────────────────────────────────────────────────────────────

def _mis_pl(mis, lbl):
    view   = st.radio("View", ["Actual","Budget","Last Year"], horizontal=True, key="pl_view")
    vkey   = {"Actual":"act","Budget":"bud","Last Year":"ly"}[view]
    ytd_key= {"Actual":"ya","Budget":"yb","Last Year":"yl"}[view]
    act    = mis["active"]
    mcols  = [lbl[i] for i in range(act)] if view=="Actual" else lbl

    PL = [
        # (display label, mis key or None, bold)
        ("REVENUE",                    None,               True),
        ("Room Revenue",               "room_rev",         False),
        ("F&B Revenue",                "fb_rev",           False),
        ("Nikaay (Spa)",               "nikaay_rev",       False),
        ("Travel Desk",                "travel_desk",      False),
        ("Curio Shop",                 "curio",            False),
        ("Adventure Sports",           "adv_sports",       False),
        ("Activity",                   "activity",         False),
        ("Laundry",                    "laundry",          False),
        ("Coffee Experience",          "coffee_exp",       False),
        ("Coffee Store",               "coffee_store",     False),
        ("Estate",                     "estate",           False),
        ("Other Departments",          "other_depts",      False),
        ("TOTAL REVENUE",              "total_rev",        True),
        ("",                           None,               False),
        ("PAYROLL",                    None,               True),
        ("Rooms Division",             "pay_rooms",        False),
        ("F&B",                        "pay_fb",           False),
        ("Nikaay",                     "pay_nikaay",       False),
        ("Travel Desk",                "pay_td",           False),
        ("Administration",             "pay_admin",        False),
        ("IT",                         "pay_it",           False),
        ("POMEC",                      "pay_pomec",        False),
        ("HR",                         "pay_hr",           False),
        ("TOTAL PAYROLL",              "total_payroll",    True),
        ("",                           None,               False),
        ("OTHER EXPENSES",             None,               True),
        ("Sales & Marketing",          "exp_sm",           False),
        ("Administration",             "exp_admin",        False),
        ("Information Technology",     "exp_it",           False),
        ("Energy Cost",                "exp_energy",       False),
        ("POMEC",                      "exp_pomec",        False),
        ("HR",                         "exp_hr",           False),
        ("TOTAL OTHER EXPENSES",       "total_other_exp",  True),
        ("",                           None,               False),
        ("GOP",                        "gop",              True),
        ("",                           None,               False),
        ("FIXED EXPENSES",             None,               True),
        ("Finance Cost",               "fix_finance",      False),
        ("Depreciation",               "fix_depr",         False),
        ("Property Tax",               "fix_prop_tax",     False),
        ("Insurance",                  "fix_insurance",    False),
        ("TOTAL FIXED EXPENSES",       "total_fixed_exp",  True),
        ("",                           None,               False),
        ("NOP BEFORE TAX",             "nop",              True),
    ]
    BOLD_SET = {label for label,_,bold in PL if bold and label}

    rows = []
    for label, key, _ in PL:
        if key is None:
            row = {"Line Item": label, **{mc: "" for mc in mcols}, "YTD": ""}
        else:
            d   = mis[key]
            vals = d[vkey]
            ytd  = d[ytd_key]
            mvals = [vals[i] for i in range(act)] if view=="Actual" else vals
            row   = {"Line Item": label}
            for mc, v in zip(mcols, mvals):
                row[mc] = "" if v == 0 else f"{v/1e7:.2f}"
            row["YTD"] = "" if ytd == 0 else f"{ytd/1e7:.2f}"
        rows.append(row)

    pl_df = pd.DataFrame(rows)

    def _style(row):
        if row["Line Item"] in BOLD_SET:
            return ["font-weight:700;background:#F0F0F0"] * len(row)
        if row["Line Item"] == "":
            return [f"background:{_BG}"] * len(row)
        return ["font-family:Lato,sans-serif;font-size:12px"] * len(row)

    st.caption(f"Values in ₹ Crores  ·  Showing: {view}")
    st.dataframe(pl_df.style.apply(_style, axis=1),
                 use_container_width=True, hide_index=True, height=820)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as wr:
        pl_df.to_excel(wr, index=False, sheet_name="P&L")
    st.download_button(f"⬇  Download {view} P&L", buf.getvalue(),
                       file_name=f"CWR_PL_{view.replace(' ','_')}.xlsx",
                       mime="application/vnd.ms-excel")


# ── Main render ───────────────────────────────────────────────────────────────

def render_cwr_mis_tab():
    up_col, info_col = st.columns([1, 2])
    with up_col:
        uploaded = st.file_uploader(
            "Upload / refresh MIS Excel",
            type=["xlsx","xls"], key="cwr_mis_upload",
            label_visibility="collapsed",
            help="Needs the 'Consolidated' sheet",
        )

    mis = None
    if uploaded:
        try:
            mis = _cached_parse(uploaded.read())
            info_col.success(f"MIS loaded: **{uploaded.name}** · {mis['active']} months of actuals")
        except Exception as e:
            st.error(f"Could not parse MIS file: {e}")
            return
    else:
        mis = load_cwr_mis()
        if mis:
            info_col.caption(f"Loaded from saved MIS · {mis['active']} months of actuals")

    if mis is None:
        st.markdown("""<div class="ops-placeholder">
          <div style="font-size:36px;margin-bottom:10px;">📊</div>
          <div style="font-size:15px;font-weight:600;">Upload CWR MIS Report</div>
          <div style="font-size:12px;margin-top:8px;color:#a09070;">
            Drop the MIS Excel above — the full dashboard loads instantly.
            Needs the <em>Consolidated</em> sheet.
          </div></div>""", unsafe_allow_html=True)
        return

    lbl = [
        f"{m} '{'25' if m in ('Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') else '26'}"
        for m in mis["months"]
    ]

    t_exec, t_rooms, t_fb, t_anc, t_costs, t_pl, t_cmp = st.tabs([
        "📊  Executive", "🛏️  Rooms", "🍽️  F&B",
        "💆  Ancillary", "💸  Costs", "📋  Full P&L", "🔍  Compare",
    ])
    with t_exec:   _mis_exec(mis, lbl)
    with t_rooms:  _mis_rooms(mis, lbl)
    with t_fb:     _mis_fb(mis, lbl)
    with t_anc:    _mis_ancillary(mis, lbl)
    with t_costs:  _mis_costs(mis, lbl)
    with t_pl:     _mis_pl(mis, lbl)
    with t_cmp:    _mis_compare(mis, lbl)


# ── Compare tab ──────────────────────────────────────────────────────────────

_CMP_KEY_MAP = {
    "Total Revenue":   "total_rev",
    "Room Revenue":    "room_rev",
    "F&B Revenue":     "fb_rev",
    "Nikaay (Spa)":    "nikaay_rev",
    "Travel Desk":     "travel_desk",
    "Activity":        "activity",
    "Total Payroll":   "total_payroll",
    "Other Expenses":  "total_other_exp",
    "GOP":             "gop",
    "Fixed Expenses":  "total_fixed_exp",
    "NOP before Tax":  "nop",
}


def _mis_compare(mis, lbl):
    st.caption("Select any line item and month — dashboard updates instantly with Actual vs Budget vs Last Year.")

    c1, c2 = st.columns(2)
    sel_item  = c1.selectbox("Line Item", CWR_LINE_ITEM_NAMES, key="cmp_item")
    sel_month = c2.selectbox(
        "Month", ["All Months"] + CWR_MONTH_OPTIONS,
        index=0, key="cmp_month",
    )

    dk, fmt = CWR_LINE_ITEM_MAP[sel_item]
    data = mis[dk]

    # ── YTD snapshot KPIs ────────────────────────────────────────────────────
    _hdr(f"{sel_item} — YTD Snapshot")
    k1, k2, k3 = st.columns(3)
    bd = _pct_var(data["ya"], data["yb"])
    ld = _pct_var(data["ya"], data["yl"])
    k1.metric("YTD Actual",    _fmt_val(data["ya"], fmt))
    k2.metric("YTD Budget",    _fmt_val(data["yb"], fmt),
              delta=f"{bd:+.1f}% vs Budget" if bd else None)
    k3.metric("YTD Last Year", _fmt_val(data["yl"], fmt),
              delta=f"{ld:+.1f}% vs LY" if ld else None)
    st.markdown("")

    # ── Monthly trend chart ──────────────────────────────────────────────────
    mi_sel = None
    if sel_month not in ("All Months", "YTD"):
        mi_sel = CWR_MONTH_OPTIONS.index(sel_month)

    bar_c = [GOLD if (mi_sel is None or i == mi_sel) else "#ddc980" for i in range(12)]
    ay  = _scale(data["act"], fmt)
    by_ = _scale(data["bud"], fmt)
    ly_ = _scale(data["ly"],  fmt)

    _hdr(f"{sel_item} — Monthly Trend  (Actual vs Budget vs Last Year)")
    fig1 = go.Figure()
    fig1.add_bar(name="Actual", x=lbl, y=ay, marker_color=bar_c, opacity=.9)
    if any(by_):
        fig1.add_scatter(name="Budget",    x=lbl, y=by_, mode="lines+markers",
                         line=dict(color=_GREY,dash="dot",width=1.5), marker=dict(size=5))
    if any(ly_):
        fig1.add_scatter(name="Last Year", x=lbl, y=ly_, mode="lines+markers",
                         line=dict(color=MAROON,dash="dash",width=1.5), marker=dict(size=5))
    fig1.update_layout(
        title=dict(text=f"{sel_item}" + (f" — {sel_month} highlighted" if mi_sel is not None else ""),
                   font=dict(family="Playfair Display", size=13, color=NAVY)),
        yaxis_title=_y_label(fmt),
        **{k:v for k,v in _lo(300).items() if k!="margin"},
        margin=dict(l=10,r=10,t=45,b=10),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Month snapshot (when a specific month is selected) ───────────────────
    if mi_sel is not None:
        _hdr(f"{sel_item} — {sel_month}  :  Actual vs Budget vs Last Year")
        av = data["act"][mi_sel]
        bv = data["bud"][mi_sel]
        lv = data["ly"][mi_sel]
        sv1, sv2, sv3 = st.columns(3)
        sv1.metric("Actual",    _fmt_val(av, fmt))
        sv2.metric("Budget",    _fmt_val(bv, fmt),
                   delta=f"{_pct_var(av,bv):+.1f}% vs Budget" if _pct_var(av,bv) else None)
        sv3.metric("Last Year", _fmt_val(lv, fmt),
                   delta=f"{_pct_var(av,lv):+.1f}% vs LY" if _pct_var(av,lv) else None)

        snap_y   = _scale([av, bv, lv], fmt)
        snap_lbl = ["Actual", "Budget", "Last Year"]
        fig2 = go.Figure()
        fig2.add_bar(
            x=snap_lbl, y=snap_y,
            marker_color=[GOLD, _GREY, MAROON], opacity=.9,
            text=[_fmt_val(v, fmt) for v in [av, bv, lv]],
            textposition="outside",
        )
        fig2.update_layout(
            showlegend=False, yaxis_title=_y_label(fmt),
            paper_bgcolor=_BG, plot_bgcolor=_PBG,
            font=dict(family="Lato",color=_TXT,size=12),
            margin=dict(l=10,r=10,t=10,b=10), height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── YTD variance bar: multiple line items ────────────────────────────────
    _hdr("YTD Variance Overview — Key Line Items  (Actual vs Budget vs Last Year)")
    items_to_show  = list(_CMP_KEY_MAP.keys())
    act_vals  = [mis[_CMP_KEY_MAP[k]]["ya"] / 1e7 for k in items_to_show]
    bud_vals  = [mis[_CMP_KEY_MAP[k]]["yb"] / 1e7 for k in items_to_show]
    ly_vals   = [mis[_CMP_KEY_MAP[k]]["yl"] / 1e7 for k in items_to_show]
    fig3 = go.Figure()
    fig3.add_bar(name="Actual",    x=items_to_show, y=act_vals, marker_color=GOLD,   opacity=.9)
    fig3.add_bar(name="Budget",    x=items_to_show, y=bud_vals, marker_color=_GREY,  opacity=.75)
    fig3.add_bar(name="Last Year", x=items_to_show, y=ly_vals,  marker_color=MAROON, opacity=.75)
    fig3.update_layout(barmode="group", yaxis_title="₹ Crores", **_lo(320))
    st.plotly_chart(fig3, use_container_width=True)

    # ── Budget variance heatmap-style table ──────────────────────────────────
    _hdr("Monthly Budget Variance — Selected Line Item (Actual vs Budget)")
    var_vals = []
    for i, m in enumerate(lbl):
        av = data["act"][i]
        bv = data["bud"][i]
        pv = _pct_var(av, bv)
        var_vals.append({
            "Month": m,
            "Actual": _fmt_val(av, fmt),
            "Budget": _fmt_val(bv, fmt),
            "Var %":  f"{pv:+.1f}%" if pv else "—",
            "Var ₹":  f"{(av-bv)/1e7:+.2f} Cr" if fmt == "cr" and bv else "—",
        })
    var_df = pd.DataFrame(var_vals)

    def _colour_var(val):
        if val == "—" or not isinstance(val, str) or not val.startswith(("+", "-")):
            return ""
        num = float(val.replace("%","").replace(" Cr","").replace(",",""))
        if num > 0:  return "color: #2d7a4f; font-weight:600"
        if num < 0:  return "color: #c0392b; font-weight:600"
        return ""

    styled = var_df.style.map(_colour_var, subset=["Var %", "Var ₹"])
    st.dataframe(styled, use_container_width=True, hide_index=True)


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
        <div style="border-left:4px solid {color}; padding:12px 18px; background:#F8F8F8;
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
