import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
    df["장르"] = df["genre"].str.split("|").str[0]
    return df


df = load_data()

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
st.text_input("이 그래프로 알 수 있는 것", key="note1")

st.divider()

# ── 그래프 2. 장르 안 영화 - 트리맵 ──
st.header("2. 장르 안에서 어떤 영화가 컸나 (트리맵)")
fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
    hover_data={"total_audi": True},
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>"
)
st.plotly_chart(fig2, width="stretch")
st.text_input("이 그래프로 알 수 있는 것", key="note2")

st.divider()

# ── 그래프 3. 총 관객 히스토그램 ──
st.header("3. 영화 대부분은 관객이 몇 명쯤인가 (히스토그램)")
fig3 = px.histogram(df, x="total_audi", nbins=30)
fig3.update_layout(xaxis_title="총 관객수", yaxis_title="영화 편수")
st.plotly_chart(fig3, width="stretch")

threshold = 1_000_000
under_1m = (df["total_audi"] < threshold).sum()
top_movie = df.loc[df["total_audi"].idxmax()]
st.caption(
    f"216편 중 {under_1m}편이 총 관객 {threshold:,}명에 못 미쳐 낮은 구간에 몰려 있습니다. "
    f"가장 관객이 많은 영화는 '{top_movie['movieNm']}'({top_movie['total_audi']:,}명)입니다."
)
st.text_input("이 그래프로 알 수 있는 것", key="note3")

st.divider()

# ── 그래프 4. 스크린수 vs 총 관객 산점도 ──
st.header("4. 스크린을 많이 받은 영화가 관객도 많나 (산점도)")
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
)
fig4.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
st.plotly_chart(fig4, width="stretch")
st.text_input("이 그래프로 알 수 있는 것", key="note4")

st.divider()

# ── 그래프 5. 장르별 박스플롯 ──
st.header("5. 장르별 관객 분포는 어떻게 다른가 (박스플롯)")
genre_counts_full = df["장르"].value_counts()
big_genres = genre_counts_full[genre_counts_full >= 10].index
df_box = df[df["장르"].isin(big_genres)]

fig5 = px.box(
    df_box,
    x="장르",
    y="total_audi",
    hover_data=["movieNm"],
    points="outliers",
)
fig5.update_traces(hovertemplate="%{customdata[0]}<br>총 관객: %{y:,}명<extra></extra>")
fig5.update_layout(yaxis_title="총 관객수")
st.plotly_chart(fig5, width="stretch")
st.caption("영화가 10편 이상인 장르만 표시했습니다.")
st.text_input("이 그래프로 알 수 있는 것", key="note5")

st.divider()

# ── 그래프 6. 버블 (산점도 + 첫 주 관객 크기) ──
st.header("6. 첫 주 관객까지 넣으면 무엇이 더 보이나 (버블)")
fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="장르",
    hover_name="movieNm",
    size_max=45,
)
fig6.update_layout(xaxis_title="개봉일 스크린수", yaxis_title="총 관객수")
st.plotly_chart(fig6, width="stretch")
st.text_input("이 그래프로 알 수 있는 것", key="note6")

st.divider()

# ── 그래프 7. 국가 → 장르 선버스트 ──
st.header("7. 국가에서 장르로 내려가면 무엇이 보이나 (선버스트)")
fig7 = px.sunburst(
    df,
    path=["nation", "장르"],
    values=None,  # 편수 기준 (기본: 행 개수)
)
fig7.update_traces(hovertemplate="%{label}<br>%{value}편<extra></extra>")
st.plotly_chart(fig7, width="stretch")
st.text_input("이 그래프로 알 수 있는 것", key="note7")

st.divider()

# ── 그래프 8. 나만의 질문 - 10위권 체류일수 vs 총 관객 산점도 ──
my_question = "10위권에 오래 머문 영화는 총 관객도 많은가"
st.header(f"8. {my_question} (산점도)")
fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",
    title=my_question,
)
fig8.update_layout(xaxis_title="10위권에 머문 날수", yaxis_title="총 관객수")
st.plotly_chart(fig8, width="stretch")
st.caption(f"내 질문: {my_question}")
st.text_input("이 그래프로 알 수 있는 것", key="note8")
