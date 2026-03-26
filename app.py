import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Noto+Sans+KR:wght@300;400;700&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --border: #1e1e2e;
    --accent: #00e5ff;
    --accent2: #ff6b6b;
    --accent3: #a78bfa;
    --green: #00ff87;
    --red: #ff4757;
    --text: #e2e8f0;
    --muted: #64748b;
    --gold: #ffd700;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'DM Mono', monospace;
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    transition: border-color 0.2s;
}
[data-testid="metric-container"]:hover { border-color: var(--accent); }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 11px !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'DM Mono', monospace !important; }
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; }

/* Buttons */
.stButton > button {
    background: transparent;
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: var(--accent);
    color: #000;
}

/* Selectbox / Multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Section headers */
.section-header {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d1117 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'DM Mono', monospace;
    font-size: 26px;
    font-weight: 500;
    color: var(--text);
    margin: 0 0 4px 0;
}
.hero-subtitle {
    font-size: 13px;
    color: var(--muted);
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,229,255,0.1);
    color: var(--accent);
    border: 1px solid rgba(0,229,255,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* Rank badge */
.rank-positive { color: var(--green); font-family: 'DM Mono', monospace; font-weight: 500; }
.rank-negative { color: var(--red); font-family: 'DM Mono', monospace; font-weight: 500; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.05em;
    border-bottom: 2px solid transparent;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: transparent !important;
}

/* Table */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Stock Universe ────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":     "005930.KS",
    "SK하이닉스":   "000660.KS",
    "LG에너지솔루션":"373220.KS",
    "삼성바이오로직스":"207940.KS",
    "현대차":        "005380.KS",
    "POSCO홀딩스":   "005490.KS",
    "NAVER":         "035420.KS",
    "카카오":        "035720.KS",
    "셀트리온":      "068270.KS",
    "기아":          "000270.KS",
}

US_STOCKS = {
    "Apple":     "AAPL",
    "NVIDIA":    "NVDA",
    "Microsoft": "MSFT",
    "Amazon":    "AMZN",
    "Tesla":     "TSLA",
    "Google":    "GOOGL",
    "Meta":      "META",
    "Netflix":   "NFLX",
    "AMD":       "AMD",
    "Berkshire": "BRK-B",
}

INDICES = {
    "KOSPI":    "^KS11",
    "KOSDAQ":   "^KQ11",
    "S&P 500":  "^GSPC",
    "NASDAQ":   "^IXIC",
    "Dow Jones":"^DJI",
}

PERIOD_MAP = {
    "1개월":  ("1mo",  "1d"),
    "3개월":  ("3mo",  "1d"),
    "6개월":  ("6mo",  "1d"),
    "1년":   ("1y",   "1wk"),
    "2년":   ("2y",   "1wk"),
    "5년":   ("5y",   "1mo"),
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,18,26,0.5)",
    font=dict(family="DM Mono, Noto Sans KR, monospace", color="#94a3b8", size=11),
    xaxis=dict(showgrid=True, gridcolor="#1e1e2e", linecolor="#1e1e2e", tickfont_size=10),
    yaxis=dict(showgrid=True, gridcolor="#1e1e2e", linecolor="#1e1e2e", tickfont_size=10),
    legend=dict(bgcolor="rgba(18,18,26,0.8)", bordercolor="#1e1e2e", borderwidth=1, font_size=11),
    margin=dict(t=40, b=40, l=60, r=20),
)

COLORS = ["#00e5ff", "#ff6b6b", "#a78bfa", "#00ff87", "#ffd700",
          "#ff9f43", "#54a0ff", "#ff6348", "#2ed573", "#eccc68"]

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        return info if info else {}
    except Exception:
        return {}

def calc_return(df: pd.DataFrame) -> float | None:
    if df.empty or len(df) < 2:
        return None
    first = df["Close"].iloc[0]
    last  = df["Close"].iloc[-1]
    if first == 0:
        return None
    return float((last - first) / first * 100)

def fmt_pct(v):
    if v is None:
        return "N/A"
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow} {abs(v):.2f}%"

def color_pct(v):
    if v is None:
        return "rank-positive"
    return "rank-positive" if v >= 0 else "rank-negative"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-header">⚙ 설정</p>', unsafe_allow_html=True)

    period_label = st.selectbox("조회 기간", list(PERIOD_MAP.keys()), index=3)
    period, interval = PERIOD_MAP[period_label]

    st.markdown("---")
    st.markdown('<p class="section-header">🇰🇷 한국 주식</p>', unsafe_allow_html=True)
    kr_selected = st.multiselect(
        "종목 선택", list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대차", "NAVER"],
    )

    st.markdown("---")
    st.markdown('<p class="section-header">🇺🇸 미국 주식</p>', unsafe_allow_html=True)
    us_selected = st.multiselect(
        "종목 선택", list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla", "Microsoft"],
    )

    st.markdown("---")
    st.markdown('<p class="section-header">📊 지수</p>', unsafe_allow_html=True)
    idx_selected = st.multiselect(
        "지수 선택", list(INDICES.keys()),
        default=["KOSPI", "S&P 500"],
    )

    st.markdown("---")
    show_volume   = st.toggle("거래량 표시", value=True)
    show_ma       = st.toggle("이동평균선 표시", value=True)
    normalize_ret = st.toggle("수익률 기준으로 정규화", value=True,
                              help="모든 종목의 시작값을 100으로 맞춰 수익률 비교")

# ── Build selected list ───────────────────────────────────────────────────────
selected = {}
for name in kr_selected:
    selected[f"🇰🇷 {name}"] = KR_STOCKS[name]
for name in us_selected:
    selected[f"🇺🇸 {name}"] = US_STOCKS[name]
for name in idx_selected:
    selected[f"📊 {name}"] = INDICES[name]

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-badge">Global Stock Dashboard</div>
  <p class="hero-title">📈 한·미 주식 비교 대시보드</p>
  <p class="hero-subtitle">
    Korean &amp; US markets · {period_label} 조회 · {len(selected)}개 종목 선택됨 ·
    마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  </p>
</div>
""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not selected:
    st.info("👈 사이드바에서 종목을 하나 이상 선택해주세요.")
    st.stop()

# ── Data Fetch ────────────────────────────────────────────────────────────────
with st.spinner("📡 데이터 불러오는 중..."):
    data: dict[str, pd.DataFrame] = {}
    returns: dict[str, float | None] = {}
    for label, ticker in selected.items():
        df = fetch_history(ticker, period, interval)
        data[label] = df
        returns[label] = calc_return(df)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  수익률 비교",
    "🕯  개별 차트",
    "🏆  성과 랭킹",
    "🔍  상세 정보",
])

# ══ TAB 1 : 수익률 비교 ═══════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">수익률 추이 비교</p>', unsafe_allow_html=True)

    fig = go.Figure()
    for i, (label, df) in enumerate(data.items()):
        if df.empty:
            continue
        close = df["Close"].dropna()
        y = (close / close.iloc[0] * 100) if normalize_ret else close
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=close.index, y=y, name=label,
            mode="lines", line=dict(color=color, width=2),
            hovertemplate=f"<b>{label}</b><br>%{{x|%Y-%m-%d}}<br>{'수익률: %{y:.1f}' if normalize_ret else '가격: %{y:,.2f}'}<extra></extra>",
        ))

    fig.update_layout(
        **PLOTLY_THEME,
        height=460,
        yaxis_title="수익률 (시작=100)" if normalize_ret else "가격",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Bar chart returns ──
    st.markdown('<p class="section-header">기간 수익률 바 차트</p>', unsafe_allow_html=True)
    bar_labels = [l for l, v in returns.items() if v is not None]
    bar_values = [returns[l] for l in bar_labels]
    bar_colors = ["#00ff87" if v >= 0 else "#ff4757" for v in bar_values]

    fig2 = go.Figure(go.Bar(
        x=bar_labels, y=bar_values,
        marker_color=bar_colors,
        text=[f"{v:+.2f}%" for v in bar_values],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>수익률: %{y:.2f}%<extra></extra>",
    ))
    fig2.update_layout(
        **PLOTLY_THEME, height=360,
        yaxis_title="수익률 (%)",
        yaxis_zeroline=True, yaxis_zerolinecolor="#1e1e2e",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── KPI row ──
    st.markdown('<p class="section-header">주요 지표</p>', unsafe_allow_html=True)
    valid = {l: v for l, v in returns.items() if v is not None}
    if valid:
        cols = st.columns(min(len(valid), 5))
        for i, (label, ret) in enumerate(list(valid.items())[:5]):
            with cols[i % 5]:
                delta_str = f"{ret:+.2f}%"
                st.metric(label=label, value=fmt_pct(ret), delta=delta_str)

# ══ TAB 2 : 개별 캔들 차트 ════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">개별 종목 캔들스틱 차트</p>', unsafe_allow_html=True)

    chart_target = st.selectbox(
        "차트 볼 종목 선택",
        [l for l, df in data.items() if not df.empty and all(c in df.columns for c in ["Open","High","Low","Close"])],
    )

    if chart_target:
        df_c = data[chart_target].copy()
        # Flatten MultiIndex if present
        if isinstance(df_c.columns, pd.MultiIndex):
            df_c.columns = df_c.columns.get_level_values(0)

        rows = 3 if show_volume else 2
        row_heights = [0.6, 0.2, 0.2] if show_volume else [0.7, 0.3]
        subplot_titles = ["캔들스틱", "거래량", "RSI"] if show_volume else ["캔들스틱", "RSI"]

        fig3 = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            row_heights=row_heights,
            vertical_spacing=0.04,
            subplot_titles=subplot_titles,
        )

        # Candlestick
        fig3.add_trace(go.Candlestick(
            x=df_c.index,
            open=df_c["Open"], high=df_c["High"],
            low=df_c["Low"],   close=df_c["Close"],
            name="캔들", increasing_line_color="#00ff87",
            decreasing_line_color="#ff4757",
        ), row=1, col=1)

        # Moving Averages
        if show_ma and len(df_c) > 20:
            for ma, color in [(20, "#00e5ff"), (60, "#ffd700"), (120, "#a78bfa")]:
                if len(df_c) > ma:
                    fig3.add_trace(go.Scatter(
                        x=df_c.index,
                        y=df_c["Close"].rolling(ma).mean(),
                        mode="lines", name=f"MA{ma}",
                        line=dict(color=color, width=1.2, dash="dot"),
                    ), row=1, col=1)

        # Volume
        vol_row = 2
        if show_volume and "Volume" in df_c.columns:
            vol_colors = ["#00ff87" if c >= o else "#ff4757"
                          for c, o in zip(df_c["Close"], df_c["Open"])]
            fig3.add_trace(go.Bar(
                x=df_c.index, y=df_c["Volume"],
                name="거래량", marker_color=vol_colors, opacity=0.7,
            ), row=2, col=1)
            vol_row = 3

        # RSI
        delta = df_c["Close"].diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        rsi   = 100 - (100 / (1 + rs))
        fig3.add_trace(go.Scatter(
            x=df_c.index, y=rsi, name="RSI(14)",
            line=dict(color="#ff9f43", width=1.5),
        ), row=vol_row, col=1)
        for lvl, clr in [(70, "#ff4757"), (30, "#00ff87")]:
            fig3.add_hline(y=lvl, line_dash="dash", line_color=clr, opacity=0.5, row=vol_row, col=1)

        fig3.update_layout(
            **PLOTLY_THEME, height=700,
            xaxis_rangeslider_visible=False,
            title=dict(text=chart_target, font=dict(color="#e2e8f0", size=14)),
        )
        st.plotly_chart(fig3, use_container_width=True)

# ══ TAB 3 : 성과 랭킹 ═════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">성과 랭킹 테이블</p>', unsafe_allow_html=True)

    rank_data = []
    for label, ret in returns.items():
        df_r = data[label]
        if df_r.empty:
            continue
        close = df_r["Close"].dropna()
        if len(close) < 2:
            continue
        vol_20 = close.pct_change().rolling(20).std().iloc[-1] * 100 * (252 ** 0.5) if len(close) >= 20 else None
        high_52 = close.max()
        low_52  = close.min()
        curr    = float(close.iloc[-1])
        from_high = (curr - high_52) / high_52 * 100

        market = "🇰🇷 한국" if "🇰🇷" in label else ("📊 지수" if "📊" in label else "🇺🇸 미국")
        rank_data.append({
            "종목": label,
            "시장": market,
            "현재가": f"{curr:,.2f}",
            f"{period_label} 수익률": ret,
            "변동성(연환산)": vol_20,
            "52주 고점 대비": from_high,
        })

    if rank_data:
        df_rank = pd.DataFrame(rank_data).sort_values(f"{period_label} 수익률", ascending=False).reset_index(drop=True)
        df_rank.index += 1

        # Styled display
        def color_val(val):
            if isinstance(val, float):
                color = "#00ff87" if val >= 0 else "#ff4757"
                return f"color: {color}; font-family: 'DM Mono', monospace"
            return ""

        styled = df_rank.style\
            .applymap(color_val, subset=[f"{period_label} 수익률", "변동성(연환산)", "52주 고점 대비"])\
            .format({
                f"{period_label} 수익률": lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A",
                "변동성(연환산)": lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A",
                "52주 고점 대비": lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A",
            })\
            .set_properties(**{"background-color": "#12121a", "color": "#e2e8f0", "border-color": "#1e1e2e"})

        st.dataframe(styled, use_container_width=True, height=420)

        # Scatter: 수익률 vs 변동성
        st.markdown('<p class="section-header">수익률 vs 변동성 (리스크-수익 맵)</p>', unsafe_allow_html=True)
        df_sc = df_rank.dropna(subset=["변동성(연환산)"])
        if not df_sc.empty:
            fig4 = px.scatter(
                df_sc,
                x="변동성(연환산)", y=f"{period_label} 수익률",
                text="종목", color="시장",
                color_discrete_map={"🇰🇷 한국": "#00e5ff", "🇺🇸 미국": "#ff6b6b", "📊 지수": "#a78bfa"},
                size_max=14,
            )
            fig4.update_traces(textposition="top center", marker=dict(size=10, opacity=0.85))
            fig4.add_hline(y=0, line_dash="dash", line_color="#1e1e2e")
            fig4.update_layout(
                **PLOTLY_THEME, height=420,
                xaxis_title="연환산 변동성 (%)",
                yaxis_title=f"{period_label} 수익률 (%)",
            )
            st.plotly_chart(fig4, use_container_width=True)

# ══ TAB 4 : 상세 정보 ═════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">종목 상세 정보</p>', unsafe_allow_html=True)

    info_target = st.selectbox(
        "상세 정보 볼 종목",
        [l for l, df in data.items() if not df.empty],
        key="info_sel",
    )

    if info_target:
        ticker_str = selected[info_target]
        info = fetch_info(ticker_str)

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            ("시가총액", info.get("marketCap"), lambda v: f"${v/1e9:.1f}B" if v else "N/A"),
            ("PER",       info.get("trailingPE"), lambda v: f"{v:.1f}x" if v else "N/A"),
            ("PBR",       info.get("priceToBook"), lambda v: f"{v:.2f}x" if v else "N/A"),
            ("배당수익률", info.get("dividendYield"), lambda v: f"{v*100:.2f}%" if v else "N/A"),
            ("52주 최고",  info.get("fiftyTwoWeekHigh"), lambda v: f"{v:,.2f}" if v else "N/A"),
            ("52주 최저",  info.get("fiftyTwoWeekLow"),  lambda v: f"{v:,.2f}" if v else "N/A"),
            ("애널리스트 목표가", info.get("targetMeanPrice"), lambda v: f"{v:,.2f}" if v else "N/A"),
            ("베타(β)",   info.get("beta"), lambda v: f"{v:.2f}" if v else "N/A"),
        ]
        cols_inf = st.columns(4)
        for i, (label, val, fmt) in enumerate(metrics):
            with cols_inf[i % 4]:
                st.metric(label=label, value=fmt(val))

        # Business summary
        summary = info.get("longBusinessSummary", "")
        if summary:
            st.markdown("---")
            st.markdown("**기업 소개**")
            st.markdown(f'<p style="color:#94a3b8; font-size:13px; line-height:1.7">{summary[:600]}{"..." if len(summary)>600 else ""}</p>', unsafe_allow_html=True)

        # Recent price table
        st.markdown("---")
        st.markdown('<p class="section-header">최근 가격 데이터</p>', unsafe_allow_html=True)
        df_show = data[info_target].copy()
        if isinstance(df_show.columns, pd.MultiIndex):
            df_show.columns = df_show.columns.get_level_values(0)
        display_cols = [c for c in ["Open","High","Low","Close","Volume"] if c in df_show.columns]
        st.dataframe(
            df_show[display_cols].tail(20).sort_index(ascending=False).style.set_properties(**{
                "background-color": "#12121a", "color": "#e2e8f0", "border-color": "#1e1e2e"
            }),
            use_container_width=True, height=380,
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#334155; font-size:11px; font-family:\'DM Mono\', monospace; letter-spacing:0.08em">'
    'GLOBAL STOCK DASHBOARD · Powered by yfinance &amp; Streamlit · 투자 참고용이며 실제 투자 권유가 아닙니다'
    '</p>',
    unsafe_allow_html=True,
)
