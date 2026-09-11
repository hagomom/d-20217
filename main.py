from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import streamlit as st

# 페이지 설정 (제목, 와이드 레이아웃)
st.set_page_config(page_title="어제 박스오피스 순위", layout="wide")


# API 결과를 1시간(3600초) 동안 캐싱하는 함수
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, date_str):
    """KOBIS API를 호출하여 전달받은 날짜의 박스오피스 데이터를 가져옵니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": date_str}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 네트워크 에러 시 예외 발생
        return response.json()
    except requests.exceptions.RequestException:
        # 통신 자체가 실패한 경우 None 반환
        return None


# 메인 화면 타이틀
st.title("🎬 어제일자 일별 박스오피스")

# 1. secrets에서 API 키 불러오기 확인
if "KOBIS_KEY" not in st.secrets:
    st.error(
        "🔑 **인증키 오류**: Streamlit Secrets에 `KOBIS_KEY` 설정이 없습니다."
    )
    st.info(
        "Streamlit Cloud의 App Settings > Secrets 메뉴에서 `KOBIS_KEY = '발급받은키'`를 등록해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 2. 한국 시간(KST) 기준 '어제' 날짜 자동 계산
# 서버 시계와 관계없이 UTC+9 시차를 적용합니다.
kst_tz = timezone(timedelta(hours=9))
now_kst = datetime.now(kst_tz)
yesterday_kst = now_kst - timedelta(days=1)
target_dt = yesterday_kst.strftime("%Y%m%d")
formatted_date = yesterday_kst.strftime("%Y년 %m월 %d일")

st.caption(f"조회 기준일 (한국 시간): {formatted_date}")

# 3. API 데이터 조회
data = fetch_box_office_data(api_key, target_dt)

# 4. 예외 및 오류 처리
if data is None:
    st.error("❌ 서버 통신 실패: API 요청 중 네트워크 오류가 발생했습니다.")
    st.info("💡 인터넷 연결 상태나 KOBIS API 서버 점검 여부를 확인해 보세요.")

elif "faultInfo" in data:
    # KOBIS API에서 인증 오류 등이 발생했을 때 보냄
    fault = data["faultInfo"]
    st.error(
        f"⚠️ API 오류 응답: {fault.get('message', '알 수 없는 오류가 발생했습니다.')}"
    )
    st.info(
        f"- 오류 코드: `{fault.get('errorCode', 'N/A')}`\n"
        "- **확인사항**: 입력한 `KOBIS_KEY`가 올바른지, 사용량이 초과되지 않았는지 확인해 주세요."
    )

else:
    # 성공 응답 구조에서 영화 목록 추출
    box_office_result = data.get("boxOfficeResult", {})
    movie_list = box_office_result.get("dailyBoxOfficeList", [])

    if not movie_list:
        st.warning(
            "⚠️ 조회된 영화 데이터가 없습니다. (어제자 집계가 완료되지 않았을 수 있습니다.)"
        )
        st.info(
            "💡 보통 매일 오전에 어제 자 데이터가 집계됩니다. 잠시 후 다시 시도해 주세요."
        )

    else:
        # 데이터프레임으로 변환
        df = pd.DataFrame(movie_list)

        # 문자열로 들어오는 숫자를 정수(int) 형태로 변환
        numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
        for col in numeric_columns:
            df[col] = (
                pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            )

        # 순위 기준으로 정렬
        df = df.sort_values("rank").reset_index(drop=True)

        # --- [1위 영화 지표 카드 세 장] ---
        top_1 = df.iloc[0]
        st.subheader(f"🥇 1위: {top_1['movieNm']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("어제 관객수", f"{top_1['audiCnt']:,} 명")
        with col2:
            st.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
        with col3:
            st.metric("스크린 수", f"{top_1['scrnCnt']:,} 개")

        st.divider()

        # --- [관객수 상위 5편 막대그래프] ---
        st.subheader("📊 관객수 상위 5개 영화")
        top_5_df = df.head(5).copy()

        # 그래프 표시에 사용할 컬럼과 인덱스 정리
        chart_data = top_5_df.set_index("movieNm")[["audiCnt"]]
        chart_data.columns = ["관객수"]
        st.bar_chart(chart_data)

        st.divider()

        # --- [전체 박스오피스 순위 표] ---
        st.subheader("📋 전체 박스오피스 순위")

        # 필요한 컬럼만 추출하여 한글명으로 변경
        display_df = df[
            ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
        ].copy()
        display_df.columns = [
            "순위",
            "영화명",
            "개봉일",
            "관객수",
            "누적관객",
            "스크린수",
        ]

        # 숫자 서식을 적용하여 표로 출력
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
