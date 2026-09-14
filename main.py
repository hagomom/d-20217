import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 기본 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="박스오피스 대시보드", layout="wide")
st.title("🎬 박스오피스 대시보드")

# 데이터가 올라와 있는 CSV 파일 주소
DATA_URL = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"


# ─────────────────────────────────────────────
# [1] 데이터 불러오기 + [2] 날짜 전처리
# ─────────────────────────────────────────────
# @st.cache_data 를 붙이면, 같은 함수를 다시 호출해도
# 이미 계산해둔 결과를 재사용해서 앱이 느려지지 않아요.
# (즉, 앱이 새로고침 될 때마다 CSV를 다시 다운로드하지 않음)
@st.cache_data
def load_data():
    # 1. CSV 파일을 판다스 데이터프레임으로 불러오기
    df = pd.read_csv(DATA_URL)

    # 2. 결측치(빈 값)가 하나라도 있는 행은 통째로 삭제
    df = df.dropna()

    # 3. "기준일자" 컬럼을 문자열(yyyy-mm-dd)에서 진짜 날짜(datetime) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"], format="%Y-%m-%d")

    # 4. 기준일자 순서(오래된 날짜 → 최근 날짜)로 전체 정렬
    df = df.sort_values("기준일자").reset_index(drop=True)

    return df


# 위에서 만든 함수를 실행해서 데이터를 준비합니다.
df = load_data()


# ─────────────────────────────────────────────
# [3] 영화 선택 기능 (누적관객수 내림차순 정렬)
# ─────────────────────────────────────────────
# 같은 영화가 여러 날짜에 걸쳐 나오기 때문에,
# 영화별로 "가장 최근 누적관객수"를 기준으로 순위를 매깁니다.
movie_rank = (
    df.sort_values("기준일자")               # 날짜순 정렬
    .groupby("영화명")["누적관객수"]         # 영화명별로 묶어서
    .last()                                   # 가장 마지막(최신) 누적관객수를 가져옴
    .sort_values(ascending=False)             # 누적관객수 내림차순 정렬
)

# 정렬된 영화 이름 리스트 (중복 없이)
movie_list = movie_rank.index.tolist()

st.sidebar.header("🔍 영화 선택")
selected_movie = st.sidebar.selectbox(
    "그래프로 볼 영화를 선택하세요 (누적관객수 순)",
    movie_list,
)


# ─────────────────────────────────────────────
# [4] 선그래프 그리기 구역 1: 일별 관객수 추이
# ─────────────────────────────────────────────
st.header("1️⃣ 일별 관객수 추이")

# 선택한 영화의 데이터만 필터링
movie_df = df[df["영화명"] == selected_movie]

fig1 = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    markers=True,
)
fig1.update_layout(xaxis_title="날짜", yaxis_title="해당일 관객수")

st.plotly_chart(fig1, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")


# ─────────────────────────────────────────────
# [5] 앞으로 그래프를 추가할 구역들
#     (지금은 비어 있고, 나중에 여기에 그래프를 추가하면 됩니다)
# ─────────────────────────────────────────────
st.header("2️⃣ 누적관객수 추이 (영역차트)")

# 같은 영화(selected_movie)의 데이터를 사용해서
# 기준일자별 누적관객수 변화를 영역차트(area chart)로 그립니다.
fig2 = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 누적관객수 변화",
)
fig2.update_layout(xaxis_title="날짜", yaxis_title="누적 관객수")

st.plotly_chart(fig2, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")

st.header("3️⃣ 누적관객수 TOP 5 영화 비교 (다중 선그래프)")

# 1. "영화명"별로 TOP10(박스오피스순위 1~10)에 등장한 일수를 셉니다.
#    이 데이터는 원래 매일 TOP10만 모아둔 데이터라, 영화명이 등장한 행 수 = TOP10 등장 일수입니다.
top10_days_count = df["영화명"].value_counts()

# 2. 20일 미만으로 등장한 영화는 제외하고, 20일 이상 등장한 영화만 남깁니다.
qualified_movies = top10_days_count[top10_days_count >= 20].index

# 3. 그 중에서 누적관객수가 가장 높은 5개 영화를 고릅니다.
#    (movie_rank는 앞에서 만들어둔, 영화별 최신 누적관객수 내림차순 정렬 값입니다.)
top5_movies = movie_rank[movie_rank.index.isin(qualified_movies)].head(5).index.tolist()

# 전체 데이터(df)에서 top5 영화에 해당하는 행만 필터링
top5_df = df[df["영화명"].isin(top5_movies)]

fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별로 다른 색상 + 범례 자동 표시
    title="TOP10 20일 이상 등장 영화 중 누적관객수 상위 5개 비교",
)
fig3.update_layout(xaxis_title="날짜", yaxis_title="누적 관객수", legend_title="영화명")

st.plotly_chart(fig3, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")


# ─────────────────────────────────────────────
# [6] 기준일자별 전체 관객수 합계 계산
#     (여러 그래프에서 재사용할 수 있는 공통 데이터)
# ─────────────────────────────────────────────
# 영화 하나가 아니라, 그날 TOP10에 오른 영화들의 "해당일관객수"를 모두 더합니다.
# → 기준일자별로 그날 TOP10 전체의 관객수 합계가 나옵니다.
daily_total = (
    df.groupby("기준일자")["해당일관객수"]
    .sum()
    .reset_index()
    .rename(columns={"해당일관객수": "전체관객수"})
)


st.header("4️⃣ TOP10 전체 관객수 추이 (7일 이동평균)")

# 위에서 구한 "기준일자별 전체 관객수 합계"에 대해 7일 이동평균을 계산합니다.
# rolling(window=7): 최근 7일치 값을 이용해 평균을 구하는 방법입니다.
daily_total["7일_이동평균"] = daily_total["전체관객수"].rolling(window=7).mean()

fig4 = px.line(
    daily_total,
    x="기준일자",
    y="전체관객수",
    title="TOP10 전체 관객수 원본 vs 7일 이동평균",
)
# 원본 선은 연하게(살짝 투명하게) 표시
fig4.update_traces(name="원본(일별 합계)", line=dict(width=1), opacity=0.4, showlegend=True)

# 이동평균 선은 진하게 추가로 그려서 겹쳐 보이게 합니다.
fig4.add_scatter(
    x=daily_total["기준일자"],
    y=daily_total["7일_이동평균"],
    mode="lines",
    name="7일 이동평균",
    line=dict(width=3),
)
fig4.update_layout(xaxis_title="날짜", yaxis_title="관객수", legend_title="구분")

st.plotly_chart(fig4, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")


st.header("5️⃣ 월별 전체 관객수 (막대그래프)")

# 위에서 구한 "기준일자별 전체 관객수 합계"(daily_total)를
# 연-월(예: 2026-01) 단위로 다시 묶어서 합산합니다.
daily_total["연월"] = daily_total["기준일자"].dt.to_period("M").astype(str)

monthly_total = (
    daily_total.groupby("연월")["전체관객수"]
    .sum()
    .reset_index()
)

fig5 = px.bar(
    monthly_total,
    x="연월",
    y="전체관객수",
    title="월별 전체 관객수 합계",
)
fig5.update_layout(xaxis_title="연-월", yaxis_title="전체 관객수")

st.plotly_chart(fig5, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")


st.header("6️⃣ 캘린더 히트맵 (주차 × 요일)")

# daily_total(기준일자별 전체 관객수 합계)을 그대로 재사용합니다.
calendar_df = daily_total.copy()

# 1. 날짜에서 "요일"을 뽑습니다. (월요일=0 ~ 일요일=6 → 한글 이름으로 변환)
weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
calendar_df["요일"] = calendar_df["기준일자"].dt.dayofweek.map(lambda i: weekday_names[i])

# 2. 날짜에서 "주차"를 뽑습니다. (월요일 시작 기준 ISO 주차, 예: 2026-W05)
iso = calendar_df["기준일자"].dt.isocalendar()
calendar_df["주차라벨"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)

# 3. 마우스를 올렸을 때 보여줄 실제 날짜(yyyy-mm-dd) 문자열도 만들어둡니다.
calendar_df["날짜문자열"] = calendar_df["기준일자"].dt.strftime("%Y-%m-%d")

# 4. "요일 × 주차" 표 형태로 값(전체관객수)과 날짜(호버용)를 각각 피벗합니다.
heatmap_values = calendar_df.pivot(index="요일", columns="주차라벨", values="전체관객수")
heatmap_dates = calendar_df.pivot(index="요일", columns="주차라벨", values="날짜문자열")

# 5. 요일 순서를 월요일 → 일요일 순서로 맞춥니다.
heatmap_values = heatmap_values.reindex(weekday_names)
heatmap_dates = heatmap_dates.reindex(weekday_names)

fig6 = go.Figure(
    data=go.Heatmap(
        z=heatmap_values.values,
        x=heatmap_values.columns,
        y=heatmap_values.index,
        text=heatmap_dates.values,  # 각 칸에 해당하는 실제 날짜
        hovertemplate="날짜: %{text}<br>전체 관객수: %{z:,.0f}명<extra></extra>",
        colorscale="Reds",  # 값이 클수록(관객이 많을수록) 색이 진해짐
        colorbar=dict(title="전체 관객수"),
    )
)
fig6.update_layout(
    title="주차별 × 요일별 전체 관객수 히트맵",
    xaxis_title="주차 (연도-주차)",
    yaxis_title="요일",
)

st.plotly_chart(fig6, use_container_width=True)

# 그래프 해석 문구를 넣을 자리 (필요할 때 문장을 채워 넣으세요)
st.caption("📌 이 그래프로 알 수 있는 것: ")
