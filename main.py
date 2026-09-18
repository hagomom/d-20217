import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

NUMERIC_COLS = [
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10",
]


@st.cache_data
def load_data():
    """1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러오고,
    이후 어떤 그래프에서도 안전하게 쓸 수 있도록 형을 정리합니다."""
    df = pd.read_csv(DATA_URL)

    # 1) 숫자여야 하는 열을 강제로 숫자형으로 바꿉니다.
    #    콤마·공백 등 이상한 문자가 섞여 있어도 숫자로 못 바꾸는 값은
    #    에러 대신 NaN(결측치)으로 처리되도록 errors="coerce"를 씁니다.
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            )

    # 2) 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다.
    #    genre 자체가 비어 있는 행은 split 결과도 NaN이 되므로 아래에서 별도 처리합니다.
    df["장르"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
    df.loc[df["genre"].isna(), "장르"] = pd.NA  # 원래 NaN이던 값은 NaN으로 유지
    df["장르"] = df["장르"].replace("", pd.NA).fillna("미분류")

    # 3) 국가·영화명의 공백/결측치도 정리합니다. (트리맵·선버스트는 NaN을 못 견딥니다)
    df["nation"] = df["nation"].astype(str).str.strip().replace("nan", pd.NA).fillna("미상")
    df["movieNm"] = df["movieNm"].astype(str).str.strip()

    return df


df = load_data()

st.caption(f"전체 {len(df)}편을 불러왔습니다.")

# ── 그래프 1. 장르별 영화 편수 도넛 ──
st.header("1. 장르별 영화 편수 (도넛)")
genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,
)
fig1.update_traces(hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>")
st.plotly_chart(fig1, width="stretch")
st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note1",
    value="애니메이션과 드라마가 나란히 가장 큰 두 조각을 차지하며, 둘을 합치면 전체 영화의 절반이 넘는다.",
)

st.divider()

# ── 그래프 2. 장르 안 영화 - 트리맵 ──
st.header("2. 장르 안에서 어떤 영화가 컸나 (트리맵)")

# total_audi가 없는(NaN) 행은 트리맵 크기를 계산할 수 없으므로 이 그래프에서만 제외합니다.
df_treemap = df.dropna(subset=["장르", "movieNm", "total_audi"]).copy()
excluded_2 = len(df) - len(df_treemap)

if df_treemap.empty:
    st.warning("트리맵을 그릴 수 있는 데이터(장르·영화명·총 관객)가 없습니다.")
else:
    fig2 = px.treemap(
        df_treemap,
        path=[px.Constant("전체"), "장르", "movieNm"],
        values="total_audi",
    )
    fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>"
    )
    st.plotly_chart(fig2, width="stretch")
    if excluded_2:
        st.caption(f"장르·영화명·총 관객 중 빠진 값이 있는 {excluded_2}편은 제외했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note2",
        value="편수로는 작아 보이던 장르도 대작 한 편만 있으면 총 관객 기준에서는 큰 상자로 나타난다. 도넛(편수)과 트리맵(관객수)은 서로 다른 기준으로 같은 데이터를 보여준다.",
    )

st.divider()

# ── 그래프 3. 총 관객 히스토그램 ──
st.header("3. 영화 대부분은 관객이 몇 명쯤인가 (히스토그램)")

df_hist = df.dropna(subset=["total_audi"]).copy()
excluded_3 = len(df) - len(df_hist)

if df_hist.empty:
    st.warning("총 관객 데이터가 없어 히스토그램을 그릴 수 없습니다.")
else:
    fig3 = px.histogram(df_hist, x="total_audi", nbins=30)
    fig3.update_layout(xaxis_title="총 관객수", yaxis_title="영화 편수")
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
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note3",
        value="대부분의 영화는 총 관객 100만 명 미만의 낮은 구간에 몰려 있고, 극소수의 대작만 오른쪽 끝에 멀리 떨어져 있다.",
    )

st.divider()

# ── 그래프 4. 스크린수 vs 총 관객 산점도 ──
st.header("4. 스크린을 많이 받은 영화가 관객도 많나 (산점도)")

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
        hover_name="movieNm",
    )
    fig4.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
    st.plotly_chart(fig4, width="stretch")
    if excluded_4:
        st.caption(f"스크린수 또는 총 관객 값이 없는 {excluded_4}편은 제외했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note4",
        value="점들이 대체로 오른쪽 위로 향해 있어, 스크린을 많이 받을수록 총 관객도 많아지는 경향이 있다. 다만 그 경향에서 크게 벗어난 영화도 있다.",
    )

st.divider()

# ── 그래프 5. 장르별 박스플롯 ──
st.header("5. 장르별 관객 분포는 어떻게 다른가 (박스플롯)")

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
        hover_data=["movieNm"],
        points="outliers",
    )
    fig5.update_traces(hovertemplate="%{customdata[0]}<br>총 관객: %{y:,.0f}명<extra></extra>")
    fig5.update_layout(yaxis_title="총 관객수")
    st.plotly_chart(fig5, width="stretch")
    st.caption("영화가 10편 이상인 장르만 표시했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note5",
        value="장르마다 상자의 위치와 높이가 달라 관객 분포가 다르고, 상자 위로 멀리 튀어 나온 점들이 그 장르를 대표하는 대작이다.",
    )

st.divider()

# ── 그래프 6. 버블 (산점도 + 첫 주 관객 크기) ──
st.header("6. 첫 주 관객까지 넣으면 무엇이 더 보이나 (버블)")

df_bubble = df.dropna(subset=["first_scrn", "total_audi", "first_week_audi"]).copy()
# 버블 크기(size)는 음수를 허용하지 않으므로 혹시 있을 음수 값을 제외합니다.
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
        hover_name="movieNm",
        size_max=45,
    )
    fig6.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
    st.plotly_chart(fig6, width="stretch")
    if excluded_6:
        st.caption(f"스크린수·총 관객·첫 주 관객 중 빠진 값이 있는 {excluded_6}편은 제외했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note6",
        value="총 관객이 많은 영화일수록 원도 대체로 커서, 첫 주 흥행 성적이 최종 흥행을 상당 부분 미리 결정한다는 것을 알 수 있다.",
    )

st.divider()

# ── 그래프 7. 국가 → 장르 선버스트 ──
st.header("7. 국가에서 장르로 내려가면 무엇이 보이나 (선버스트)")

df_sun = df.dropna(subset=["nation", "장르"]).copy()
excluded_7 = len(df) - len(df_sun)

if df_sun.empty:
    st.warning("국가·장르 데이터가 부족해 선버스트를 그릴 수 없습니다.")
else:
    fig7 = px.sunburst(
        df_sun,
        path=["nation", "장르"],
    )
    fig7.update_traces(hovertemplate="%{label}<br>%{value}편<extra></extra>")
    st.plotly_chart(fig7, width="stretch")
    if excluded_7:
        st.caption(f"국가 또는 장르 값이 없는 {excluded_7}편은 제외했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note7",
        value="안쪽 고리로 어느 나라 영화가 많은지, 바깥 고리로 그 나라가 어떤 장르를 많이 만드는지 한 그래프에서 함께 볼 수 있다.",
    )

st.divider()

# ── 그래프 8. 나만의 질문 - 10위권 체류일수 vs 총 관객 산점도 ──
my_question = "10위권에 오래 머문 영화는 총 관객도 많은가"
st.header(f"8. {my_question} (산점도)")

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
        title=my_question,
    )
    fig8.update_layout(xaxis_title="10위권에 머문 날수", yaxis_title="총 관객수")
    st.plotly_chart(fig8, width="stretch")
    st.caption(f"내 질문: {my_question}")
    if excluded_8:
        st.caption(f"체류일수 또는 총 관객 값이 없는 {excluded_8}편은 제외했습니다.")
    st.text_input(
        "이 그래프로 알 수 있는 것",
        key="note8",
        value="10위권에 오래 머문 영화일수록 총 관객도 대체로 많아, 순위 체류 기간이 흥행 규모와 함께 움직이는 경향이 있다.",
    )
