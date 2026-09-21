import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────────────────────────────────────────────────────────
# 디자인 토큰 — "필름 아카이브" : 어두운 상영관 + 마퀴 조명의 골드
# ────────────────────────────────────────────────────────────────
BG = "#15130F"
BG_ELEV = "#1E1B16"
BG_CARD = "#211C16"
GOLD = "#C9A227"
GOLD_SOFT = "#E4C86B"
BURGUNDY = "#7A2035"
CREAM = "#F3EEE1"
MUTED = "#9C9382"
HAIRLINE = "rgba(201, 162, 39, 0.22)"

CINEMA_COLORS = [
    "#C9A227", "#7A2035", "#3E5C57", "#B8895F", "#8AA399",
    "#9C6B53", "#6B4E71", "#4A5859", "#C97C5D", "#5C4033",
    "#D4AF7A", "#365E5C",
]

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

NUMERIC_COLS = [
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10",
]

# ────────────────────────────────────────────────────────────────
# 페이지 설정 & 전역 CSS
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="필름 아카이브 — 영화 데이터 그래프 도감",
    page_icon="🎞️",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Song+Myung&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at 15% -10%, #221d15 0%, transparent 45%),
            """ + BG + """;
        color: """ + CREAM + """;
    }

    section[data-testid="stSidebar"] {
        background: #100E0B;
        border-right: 1px solid """ + HAIRLINE + """;
    }
    section[data-testid="stSidebar"] * { color: """ + CREAM + """; }

    /* 기본 헤더/텍스트 컬러 */
    h1, h2, h3, h4 { color: """ + CREAM + """; }
    p, li, span, label { color: """ + CREAM + """; }

    /* 구분선 숨김(커스텀 디바이더로 대체) */
    hr { border-color: """ + HAIRLINE + """ !important; }

    /* ── 히어로 ── */
    .hero {
        padding: 2.6rem 2.2rem 2.2rem 2.2rem;
        margin-bottom: 1.6rem;
        border: 1px solid """ + HAIRLINE + """;
        border-top: 3px solid """ + GOLD + """;
        border-bottom: 3px solid """ + GOLD + """;
        background: linear-gradient(180deg, """ + BG_ELEV + """ 0%, """ + BG + """ 100%);
        text-align: center;
    }
    .hero-eyebrow {
        font-size: 0.82rem;
        color: """ + MUTED + """;
        letter-spacing: 0.04em;
        margin-bottom: 0.6rem;
    }
    .hero-title {
        font-family: 'Song Myung', serif;
        font-size: 2.6rem;
        color: """ + GOLD_SOFT + """;
        margin: 0 0 0.6rem 0;
        line-height: 1.25;
    }
    .hero-tagline {
        font-size: 1.02rem;
        color: """ + MUTED + """;
        max-width: 640px;
        margin: 0 auto;
        line-height: 1.7;
    }

    /* ── 티켓 스텁 KPI 카드 ── */
    .ticket {
        border: 1px dashed """ + HAIRLINE + """;
        background: """ + BG_CARD + """;
        border-radius: 4px;
        padding: 1rem 1.1rem;
        text-align: center;
        height: 100%;
    }
    .ticket-num {
        font-family: 'Song Myung', serif;
        font-size: 1.55rem;
        color: """ + GOLD + """;
    }
    .ticket-label {
        font-size: 0.82rem;
        color: """ + MUTED + """;
        margin-top: 0.2rem;
    }

    /* ── 섹션 타이틀 (프레임 번호 + 제목) ── */
    .section-head {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.2rem 0 1.0rem 0;
    }
    .frame-badge {
        flex: none;
        width: 2.1rem;
        height: 2.1rem;
        border: 1px solid """ + GOLD + """;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.92rem;
        color: """ + GOLD + """;
    }
    .section-title {
        font-family: 'Song Myung', serif;
        font-size: 1.45rem;
        color: """ + CREAM + """;
        border-bottom: 1px solid """ + HAIRLINE + """;
        padding-bottom: 0.55rem;
        flex: 1;
        margin: 0;
    }
    .section-sub {
        color: """ + MUTED + """;
        font-size: 0.9rem;
        margin: -0.5rem 0 1rem 2.9rem;
    }

    /* ── 필름 디바이더 (스프로킷 홀) ── */
    .film-divider {
        display: flex;
        justify-content: space-between;
        margin: 2.6rem 0 2.2rem 0;
        padding: 0 0.2rem;
    }
    .film-divider span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: """ + HAIRLINE + """;
    }

    /* ── 인사이트 카드(입력창) ── */
    .insight-label {
        font-size: 0.82rem;
        color: """ + GOLD_SOFT + """;
        margin: 0.6rem 0 0.35rem 0;
    }
    .stTextInput input {
        background: """ + BG_CARD + """ !important;
        color: """ + CREAM + """ !important;
        border: 1px solid """ + HAIRLINE + """ !important;
        border-radius: 3px !important;
    }
    .stTextInput input:focus {
        border-color: """ + GOLD + """ !important;
        box-shadow: none !important;
    }

    /* 캡션(제외 편수 등) */
    [data-testid="stCaptionContainer"] p, .stCaption {
        color: """ + MUTED + """ !important;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def section_head(number: int, title: str, sub: str, anchor: str):
    st.markdown(
        f"""
        <div class="section-head" id="{anchor}">
            <div class="frame-badge">{number:02d}</div>
            <h2 class="section-title">{title}</h2>
        </div>
        <div class="section-sub">{sub}</div>
        """,
        unsafe_allow_html=True,
    )


def film_divider():
    dots = "".join("<span></span>" for _ in range(16))
    st.markdown(f'<div class="film-divider">{dots}</div>', unsafe_allow_html=True)


def insight_field(key: str, default: str):
    st.markdown('<div class="insight-label">이 그래프로 알 수 있는 것</div>', unsafe_allow_html=True)
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key=key,
        value=default,
        label_visibility="collapsed",
    )


def base_theme(fig, height=460, title=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR, sans-serif", color=CREAM, size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=HAIRLINE, borderwidth=1),
        margin=dict(l=10, r=10, t=50 if title else 30, b=10),
        height=height,
        hoverlabel=dict(bgcolor=BG_ELEV, font_color=CREAM, bordercolor=GOLD),
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(family="Song Myung, serif", color=GOLD_SOFT, size=19)))
    return fig


def axis_theme(fig):
    fig.update_xaxes(gridcolor="rgba(201,162,39,0.10)", zerolinecolor=HAIRLINE, color=MUTED, linecolor=HAIRLINE)
    fig.update_yaxes(gridcolor="rgba(201,162,39,0.10)", zerolinecolor=HAIRLINE, color=MUTED, linecolor=HAIRLINE)
    return fig


# ────────────────────────────────────────────────────────────────
# 데이터 로드 & 정제
# ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러오고,
    이후 어떤 그래프에서도 안전하게 쓸 수 있도록 형을 정리합니다."""
    df = pd.read_csv(DATA_URL)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            )

    df["장르"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
    df.loc[df["genre"].isna(), "장르"] = pd.NA
    df["장르"] = df["장르"].replace("", pd.NA).fillna("미분류")

    df["nation"] = df["nation"].astype(str).str.strip().replace("nan", pd.NA).fillna("미상")
    df["movieNm"] = df["movieNm"].astype(str).str.strip()

    return df


df = load_data()

genre_count_all = df["장르"].value_counts().reset_index()
genre_count_all.columns = ["장르", "편수"]
GENRE_COLOR_MAP = {
    genre: CINEMA_COLORS[i % len(CINEMA_COLORS)]
    for i, genre in enumerate(genre_count_all["장르"])
}

# ────────────────────────────────────────────────────────────────
# 사이드바 — 목차
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="font-family:'Song Myung',serif; font-size:1.2rem; color:%s; margin-bottom:0.2rem;">
            🎞️ 필름 아카이브
        </div>
        <div style="color:%s; font-size:0.85rem; margin-bottom:1.4rem;">
            도감 Ⅱ · 분포와 관계
        </div>
        """ % (GOLD_SOFT, MUTED),
        unsafe_allow_html=True,
    )
    nav_items = [
        ("01", "장르 구성 · 도넛", "g1"),
        ("02", "장르 안 대작 · 트리맵", "g2"),
        ("03", "관객 분포 · 히스토그램", "g3"),
        ("04", "스크린 대 관객 · 산점도", "g4"),
        ("05", "장르별 분포 · 박스플롯", "g5"),
        ("06", "첫 주 흥행 · 버블", "g6"),
        ("07", "국가 → 장르 · 선버스트", "g7"),
        ("08", "나의 질문 · 산점도", "g8"),
    ]
    for num, label, anchor in nav_items:
        st.markdown(
            f'<a href="#{anchor}" style="display:block; padding:0.35rem 0; '
            f'color:{CREAM}; text-decoration:none; font-size:0.88rem; '
            f'border-bottom:1px solid {HAIRLINE};">'
            f'<span style="color:{GOLD};">{num}</span>&nbsp;&nbsp;{label}</a>',
            unsafe_allow_html=True,
        )

# ────────────────────────────────────────────────────────────────
# 히어로
# ────────────────────────────────────────────────────────────────
total_movies = len(df)
total_audience = df["total_audi"].dropna().sum()
top_genre_row = genre_count_all.iloc[0]
top_movie_row = df.loc[df["total_audi"].idxmax()] if df["total_audi"].notna().any() else None

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">KOBIS 박스오피스 · 영화 단위 요약표</div>
        <h1 class="hero-title">영화 데이터 그래프 도감</h1>
        <p class="hero-tagline">
            시간이 아니라 분포·구성·관계를 묻는다 — 10위권에 든 {total_movies}편의 스크린 위에서.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, f"{total_movies}편", "수록 영화"),
    (k2, f"{total_audience / 1e8:.1f}억", "누적 총 관객"),
    (k3, f"{top_genre_row['장르']}", f"최다 장르 · {top_genre_row['편수']}편"),
    (k4, f"{top_movie_row['movieNm'] if top_movie_row is not None else '—'}", "최고 흥행작"),
]
for col, num, label in kpis:
    col.markdown(
        f'<div class="ticket"><div class="ticket-num">{num}</div>'
        f'<div class="ticket-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

film_divider()

# ── 그래프 1. 장르별 영화 편수 도넛 ──
section_head(1, "장르별 영화 편수", "10위권에 든 영화의 장르 구성은 어떠한가 — 도넛", "g1")

fig1 = px.pie(
    genre_count_all,
    names="장르",
    values="편수",
    hole=0.55,
    color="장르",
    color_discrete_map=GENRE_COLOR_MAP,
)
fig1.update_traces(
    hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>",
    marker=dict(line=dict(color=BG, width=2)),
    textfont=dict(color=CREAM),
)
fig1 = base_theme(fig1, height=440)
st.plotly_chart(fig1, width="stretch")
insight_field(
    "note1",
    "애니메이션과 드라마가 나란히 가장 큰 두 조각을 차지하며, 둘을 합치면 전체 영화의 절반이 넘는다.",
)

film_divider()

# ── 그래프 2. 장르 안 영화 - 트리맵 ──
section_head(2, "장르 안에서 어떤 영화가 컸나", "칸의 크기는 총 관객 — 트리맵", "g2")

df_treemap = df.dropna(subset=["장르", "movieNm", "total_audi"]).copy()
excluded_2 = len(df) - len(df_treemap)

if df_treemap.empty:
    st.warning("트리맵을 그릴 수 있는 데이터(장르·영화명·총 관객)가 없습니다.")
else:
    fig2 = px.treemap(
        df_treemap,
        path=[px.Constant("전체"), "장르", "movieNm"],
        values="total_audi",
        color_discrete_sequence=CINEMA_COLORS,
    )
    fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>",
        marker=dict(line=dict(color=BG, width=1.5)),
        root_color=BG_ELEV,
    )
    fig2 = base_theme(fig2, height=480)
    st.plotly_chart(fig2, width="stretch")
    if excluded_2:
        st.caption(f"장르·영화명·총 관객 중 빠진 값이 있는 {excluded_2}편은 제외했습니다.")
    insight_field(
        "note2",
        "편수로는 작아 보이던 장르도 대작 한 편만 있으면 총 관객 기준에서는 큰 상자로 나타난다. "
        "도넛(편수)과 트리맵(관객수)은 서로 다른 기준으로 같은 데이터를 보여준다.",
    )

film_divider()

# ── 그래프 3. 총 관객 히스토그램 ──
section_head(3, "영화 대부분은 관객이 몇 명쯤인가", "총 관객수 분포 — 히스토그램", "g3")

df_hist = df.dropna(subset=["total_audi"]).copy()
excluded_3 = len(df) - len(df_hist)

if df_hist.empty:
    st.warning("총 관객 데이터가 없어 히스토그램을 그릴 수 없습니다.")
else:
    fig3 = px.histogram(df_hist, x="total_audi", nbins=30, color_discrete_sequence=[GOLD])
    fig3.update_traces(marker=dict(line=dict(color=BG, width=0.5)))
    fig3.update_layout(xaxis_title="총 관객수", yaxis_title="영화 편수", bargap=0.08)
    fig3 = axis_theme(base_theme(fig3, height=430))
    st.plotly_chart(fig3, width="stretch")

    threshold = 1_000_000
    under_1m = (df_hist["total_audi"] < threshold).sum()
    top_movie = df_hist.loc[df_hist["total_audi"].idxmax()]
    st.caption(
        f"{len(df_hist)}편 중 {under_1m}편이 총 관객 {threshold:,}명에 못 미쳐 낮은 구간에 몰려 있습니다. "
        f"가장 관객이 많은 영화는 '{top_movie['movieNm']}'({top_movie['total_audi']:,.0f}명)입니다."
    )
    if excluded_3:
        st.caption(f"총 관객 값이 없는 {excluded_3}편은 제외했습니다.")
    insight_field(
        "note3",
        "대부분의 영화는 총 관객 100만 명 미만의 낮은 구간에 몰려 있고, 극소수의 대작만 오른쪽 끝에 멀리 떨어져 있다.",
    )

film_divider()

# ── 그래프 4. 스크린수 vs 총 관객 산점도 ──
section_head(4, "스크린을 많이 받은 영화가 관객도 많나", "개봉일 스크린수 × 총 관객 — 산점도", "g4")

df_scatter = df.dropna(subset=["first_scrn", "total_audi"]).copy()
excluded_4 = len(df) - len(df_scatter)

if df_scatter.empty:
    st.warning("스크린수·총 관객 데이터가 부족해 산점도를 그릴 수 없습니다.")
else:
    fig4 = px.scatter(
        df_scatter,
        x="first_scrn",
        y="total_audi",
        color="장르",
        color_discrete_map=GENRE_COLOR_MAP,
        hover_name="movieNm",
        opacity=0.85,
    )
    fig4.update_traces(marker=dict(size=9, line=dict(color=BG, width=0.6)))
    fig4.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
    fig4 = axis_theme(base_theme(fig4, height=470))
    st.plotly_chart(fig4, width="stretch")
    if excluded_4:
        st.caption(f"스크린수 또는 총 관객 값이 없는 {excluded_4}편은 제외했습니다.")
    insight_field(
        "note4",
        "점들이 대체로 오른쪽 위로 향해 있어, 스크린을 많이 받을수록 총 관객도 많아지는 경향이 있다. "
        "다만 그 경향에서 크게 벗어난 영화도 있다.",
    )

film_divider()

# ── 그래프 5. 장르별 박스플롯 ──
section_head(5, "장르별 관객 분포는 어떻게 다른가", "영화 10편 이상인 장르만 — 박스플롯", "g5")

df_box_base = df.dropna(subset=["장르", "total_audi"]).copy()
genre_counts_full = df_box_base["장르"].value_counts()
big_genres = genre_counts_full[genre_counts_full >= 10].index
df_box = df_box_base[df_box_base["장르"].isin(big_genres)]

if df_box.empty:
    st.warning("영화가 10편 이상인 장르가 없어 박스플롯을 그릴 수 없습니다.")
else:
    fig5 = px.box(
        df_box,
        x="장르",
        y="total_audi",
        color="장르",
        color_discrete_map=GENRE_COLOR_MAP,
        hover_data=["movieNm"],
        points="outliers",
    )
    fig5.update_traces(hovertemplate="%{customdata[0]}<br>총 관객: %{y:,.0f}명<extra></extra>")
    fig5.update_layout(yaxis_title="총 관객수", xaxis_title="", showlegend=False)
    fig5 = axis_theme(base_theme(fig5, height=470))
    st.plotly_chart(fig5, width="stretch")
    st.caption("영화가 10편 이상인 장르만 표시했습니다.")
    insight_field(
        "note5",
        "장르마다 상자의 위치와 높이가 달라 관객 분포가 다르고, 상자 위로 멀리 튀어 나온 점들이 그 장르를 대표하는 대작이다.",
    )

film_divider()

# ── 그래프 6. 버블 (산점도 + 첫 주 관객 크기) ──
section_head(6, "첫 주 관객까지 넣으면 무엇이 더 보이나", "스크린수 × 총 관객, 크기는 첫 주 관객 — 버블", "g6")

df_bubble = df.dropna(subset=["first_scrn", "total_audi", "first_week_audi"]).copy()
df_bubble = df_bubble[df_bubble["first_week_audi"] >= 0]
excluded_6 = len(df) - len(df_bubble)

if df_bubble.empty:
    st.warning("첫 주 관객 데이터가 부족해 버블 그래프를 그릴 수 없습니다.")
else:
    fig6 = px.scatter(
        df_bubble,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="장르",
        color_discrete_map=GENRE_COLOR_MAP,
        hover_name="movieNm",
        size_max=48,
        opacity=0.82,
    )
    fig6.update_traces(marker=dict(line=dict(color=BG, width=0.6)))
    fig6.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
    fig6 = axis_theme(base_theme(fig6, height=470))
    st.plotly_chart(fig6, width="stretch")
    if excluded_6:
        st.caption(f"스크린수·총 관객·첫 주 관객 중 빠진 값이 있는 {excluded_6}편은 제외했습니다.")
    insight_field(
        "note6",
        "총 관객이 많은 영화일수록 원도 대체로 커서, 첫 주 흥행 성적이 최종 흥행을 상당 부분 미리 결정한다는 것을 알 수 있다.",
    )

film_divider()

# ── 그래프 7. 국가 → 장르 선버스트 ──
section_head(7, "국가에서 장르로 내려가면 무엇이 보이나", "안쪽은 국가, 바깥쪽은 장르 — 선버스트", "g7")

df_sun = df.dropna(subset=["nation", "장르"]).copy()
excluded_7 = len(df) - len(df_sun)

if df_sun.empty:
    st.warning("국가·장르 데이터가 부족해 선버스트를 그릴 수 없습니다.")
else:
    fig7 = px.sunburst(
        df_sun,
        path=["nation", "장르"],
        color_discrete_sequence=CINEMA_COLORS,
    )
    fig7.update_traces(
        hovertemplate="%{label}<br>%{value}편<extra></extra>",
        marker=dict(line=dict(color=BG, width=1.2)),
    )
    fig7 = base_theme(fig7, height=500)
    st.plotly_chart(fig7, width="stretch")
    if excluded_7:
        st.caption(f"국가 또는 장르 값이 없는 {excluded_7}편은 제외했습니다.")
    insight_field(
        "note7",
        "안쪽 고리로 어느 나라 영화가 많은지, 바깥 고리로 그 나라가 어떤 장르를 많이 만드는지 한 그래프에서 함께 볼 수 있다.",
    )

film_divider()

# ── 그래프 8. 나만의 질문 - 10위권 체류일수 vs 총 관객 산점도 ──
my_question = "10위권에 오래 머문 영화는 총 관객도 많은가"
section_head(8, "나만의 8번째 질문", my_question, "g8")

df_q8 = df.dropna(subset=["days_in_top10", "total_audi"]).copy()
excluded_8 = len(df) - len(df_q8)

if df_q8.empty:
    st.warning("10위권 체류일수·총 관객 데이터가 부족해 그래프를 그릴 수 없습니다.")
else:
    fig8 = px.scatter(
        df_q8,
        x="days_in_top10",
        y="total_audi",
        hover_name="movieNm",
        color_discrete_sequence=[GOLD_SOFT],
    )
    fig8.update_traces(marker=dict(size=9, line=dict(color=BG, width=0.6)))
    fig8.update_layout(xaxis_title="10위권에 머문 날수", yaxis_title="총 관객수")
    fig8 = axis_theme(base_theme(fig8, height=460, title=my_question))
    st.plotly_chart(fig8, width="stretch")
    st.caption(f"내 질문: {my_question}")
    if excluded_8:
        st.caption(f"체류일수 또는 총 관객 값이 없는 {excluded_8}편은 제외했습니다.")
    insight_field(
        "note8",
        "10위권에 오래 머문 영화일수록 총 관객도 대체로 많아, 순위 체류 기간이 흥행 규모와 함께 움직이는 경향이 있다.",
    )

st.markdown(
    f'<div style="text-align:center; color:{MUTED}; font-size:0.8rem; margin-top:2rem;">'
    f"원출처 · 영화진흥위원회 KOBIS"
    f"</div>",
    unsafe_allow_html=True,
)
