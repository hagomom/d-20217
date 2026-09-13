import streamlit as st
import pandas as pd
import plotly.express as px

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
st.header("2️⃣ (추가 예정) 두 번째 그래프 구역")
# 여기에 두 번째 그래프 코드를 작성하세요.
st.caption("📌 이 그래프로 알 수 있는 것: ")

st.header("3️⃣ (추가 예정) 세 번째 그래프 구역")
# 여기에 세 번째 그래프 코드를 작성하세요.
st.caption("📌 이 그래프로 알 수 있는 것: ")
