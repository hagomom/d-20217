from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import streamlit as st

# 페이지 설정 (제목 및 와이드 레이아웃)
st.set_page_config(page_title="일별 박스오피스 조회", layout="wide")


# API 결과를 1시간(3600초) 동안 캐싱하는 함수
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, date_str):
    """KOBIS API를 호출하여 전달받은 날짜(YYYYMMDD)의 박스오피스 데이터를 가져옵니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": date_str}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 네트워크 오류 시 예외 발생
        return response.json()
    except requests.exceptions.RequestException:
        return None


# 타이틀
st.title("🎬 일별 박스오피스 조회")

# 1. secrets에서 API 인증키 확인
if "KOBIS_KEY" not in st.secrets:
    st.error(
        "🔑 **인증키 오류**: Streamlit Secrets에 `KOBIS_KEY` 설정이 없습니다."
    )
    st.info(
        "Streamlit Cloud의 App Settings > Secrets 메뉴에서 `KOBIS_KEY = '발급받은키'`를 등록해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 2. 한국 시간(KST) 기준 어제 날짜 계산 (달력의 최대 선택 한계)
kst_tz = timezone(timedelta(hours=9))
now_kst = datetime.now(kst_tz)
yesterday_kst = (now_kst - timedelta(days=1)).date()

# 달력을 통해 조회하고 싶은 날짜 선택 (오늘 이후/오늘 날짜는 선택 불가능하도록 max_value 설정)
selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요 (어제 날짜까지만 선택 가능)",
    value=yesterday_kst,
    max_value=yesterday_kst,
)

# API용 날짜 포맷 (YYYYMMDD) 및 화면 표시용 포맷 생성
target_dt = selected_date.strftime("%Y%m%d")
formatted_date = selected_date.strftime("%Y년 %m월 %d일")

st.caption(f"선택한 날짜: {formatted_date}")

# 3. API 데이터 호출
data = fetch_box_office_data(api_key, target_dt)

# 4. 예외 상황 및 결과 처리
if data is None:
    st.error("❌ 서버 통신 실패: API 요청 중 네트워크 오류가 발생했습니다.")
    st.info("💡 인터넷 연결 상태나 KOBIS API 서버 점검 여부를 확인해 보세요.")

elif "faultInfo" in data:
    # KOBIS 인증 실패 또는 API 오류 응답
    fault = data["faultInfo"]
    st.error(
        f"⚠️ API 오류 응답: {fault.get('message', '알 수 없는 오류가 발생했습니다.')}"
    )
    st.info(
        f"- 오류 코드: `{fault.get('errorCode', 'N/A')}`\n"
        "- **확인사항**: 등록된 `KOBIS_KEY`가 올바른지, 하루 사용량이 초과되지 않았는지 확인해 주세요."
    )

else:
    # 박스오피스 결과 목록 추출
    box_office_result = data.get("boxOfficeResult", {})
    movie_list = box_office_result.get("dailyBoxOfficeList", [])

    # 영화 목록이 비어있는 경우
    if not movie_list:
        st.warning("⚠️ 그날은 아직 집계 전입니다.")
        st.info("💡 다른 날짜를 선택하시거나, 집계가 완료된 후 다시 시도해 주세요.")

    else:
        # 데이터프레임으로 변환
        df = pd.DataFrame(movie_list)

        # 문자열 숫자를 정수(int) 타입으로 변환
        numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]
        for col in numeric_columns:
            df[col] = (
                pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            )

        # 순위 기준으로 정렬
        df = df.sort_values("rank").reset_index(drop=True)

        # 전날 대비 순위 증감(rankInten) 화살표 표시 함수
        def format_rank_inten(val):
            if val > 0:
                return f"🔺 {val}"  # 상승 시 빨간 위 화살표
            elif val < 0:
                return f"🔻 {abs(val)}"  # 하강 시 파란 아래 화살표
            else:
                return "-"  # 변동 없음

        df["rankIntenFormatted"] = df["rankInten"].apply(format_rank_inten)

        # 누적 관객 100만 명 이상 영화명 옆에 트로피 이모지(🏆) 추가 함수
        def format_movie_name(row):
            name = row["movieNm"]
            if row["audiAcc"] >= 1_000_000:
                return f"{name} 🏆"
            return name

        df["displayMovieNm"] = df.apply(format_movie_name, axis=1)

        # --- [1위 영화 지표 카드 세 장] ---
        top_1 = df.iloc[0]
        st.subheader(f"🥇 1위: {top_1['displayMovieNm']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("일별 관객수", f"{top_1['audiCnt']:,} 명")
        with col2:
            st.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
        with col3:
            st.metric("스크린 수", f"{top_1['scrnCnt']:,} 개")

        st.divider()

        # --- [관객수 상위 5편 막대그래프] ---
        st.subheader("📊 관객수 상위 5개 영화")
        top_5_df = df.head(5).copy()

        # 막대그래프 데이터 세팅
        chart_data = top_5_df.set_index("displayMovieNm")[["audiCnt"]]
        chart_data.columns = ["관객수"]
        st.bar_chart(chart_data)

        st.divider()

        # --- [전체 박스오피스 순위 표] ---
        st.subheader("📋 전체 박스오피스 순위")

        # 표에 보여줄 컬럼 선택 및 한글명 변경
        display_df = df[
            [
                "rank",
                "rankIntenFormatted",
                "displayMovieNm",
                "openDt",
                "audiCnt",
                "audiAcc",
                "scrnCnt",
            ]
        ].copy()

        display_df.columns = [
            "순위",
            "전날 대비",
            "영화명",
            "개봉일",
            "관객수",
            "누적관객",
            "스크린수",
        ]

        # 천 단위 쉼표 서식을 적용하여 표 출력
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순위": st.column_config.NumberColumn(format="%d위"),
                "관객수": st.column_config.NumberColumn(format="%d명"),
                "누적관객": st.column_config.NumberColumn(format="%d명"),
                "스크린수": st.column_config.NumberColumn(format="%d개"),
            },
        )
