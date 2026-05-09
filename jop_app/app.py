import streamlit as st
import requests
import pandas as pd

# 1. API 설정
# 사용자가 제공한 새로운 URL과 인증키를 적용합니다.
API_KEY = "dc305c4d0abc3cb89807335cb6775032c45c4f2942b70c74b82b705f139aa715"
BASE_URL = "https://apis.data.go.kr/1051000/recruitment/list"

def get_job_data(page_no=1, num_rows=10):
    """공공데이터 포털 API에서 채용 데이터를 가져오는 함수 (JSON 방식)"""
    params = {
        'serviceKey': requests.utils.unquote(API_KEY),
        'pageNo': page_no,
        'numOfRows': num_rows,
        'resultType': 'JSON'  # JSON 형식으로 요청
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()  # XML 변환 대신 바로 JSON 파싱
            
            # API 응답 구조에 맞게 데이터 추출
            # 알리오 API 구조: result -> list
            items = data.get('result', [])
            
            if items:
                return pd.DataFrame(items)
            else:
                return "데이터가 없습니다. (파라미터를 확인해주세요)"
        else:
            return f"API 호출 실패 (상태 코드: {response.status_code})"
            
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 2. UI 레이아웃 설정
st.set_page_config(page_title="공공기관 채용 알리미", page_icon="💼", layout="wide")

st.title("🏛️ 실시간 공공기관 채용 정보")
st.caption("기획재정부 알리오(ALIO) 채용 공고 데이터를 실시간으로 조회합니다.")
st.markdown("---")

# 사이드바 설정
st.sidebar.header("🔍 검색 설정")
page = st.sidebar.number_input("페이지 번호", min_value=1, value=1)
rows = st.sidebar.slider("조회 개수", 5, 50, 10)

# 3. 데이터 로드 및 출력
with st.spinner('데이터를 불러오는 중입니다...'):
    df = get_job_data(page, rows)

if isinstance(df, pd.DataFrame):
    # 실제 API 리턴값(필드명)에 맞춘 컬럼 매핑
    # 알리오 API의 필드명 예시: 'as_nm'(기관명), 're_title'(제목), 're_area'(지역) 등
    # API 명세서에 따라 아래 key값을 조정해야 할 수 있습니다.
    cols_to_show = {
        'instNm': '기관명',
        'title': '채용 공고명',
        'regionNm': '근무지역',
        'recruitTypeNm': '채용유형',
        'regDate': '등록일'
    }
    
    # 존재하는 컬럼만 선택하여 보여줌
    available_cols = [c for c in cols_to_show.keys() if c in df.columns]
    display_df = df[available_cols].rename(columns=cols_to_show)
    
    st.success(f"총 {len(df)}개의 공고를 찾았습니다.")
    st.dataframe(display_df, use_container_width=True)

    # 상세 정보 확인 섹션
    st.subheader("📌 공고 상세 정보")
    if not df.empty:
        selected_title = st.selectbox("조회할 공고를 선택하세요:", df['title'].unique())
        detail = df[df['title'] == selected_title].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**🏢 기관명:** {detail.get('instNm', '정보없음')}")
            st.write(f"**📍 근무지:** {detail.get('regionNm', '정보없음')}")
        with c2:
            st.write(f"**📅 등록일:** {detail.get('regDate', '정보없음')}")
            # 공고 상세 페이지 URL (있는 경우)
            link = detail.get('srcUrl', '#') 
            if link != '#':
                st.link_button("공고 원문 보기", link)
            else:
                st.write("🔗 원문 링크가 제공되지 않는 공고입니다.")

elif isinstance(df, str):
    st.warning(df)
