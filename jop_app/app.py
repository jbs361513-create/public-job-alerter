import streamlit as st
import requests
import pandas as pd
import xmltodict

# 1. API 설정
# 사용자가 제공한 인증키를 바로 적용했습니다.
API_KEY = "81f127320e9e472938369f7758c80cca9b97e544b77e4b6e690ecf8a01541b9d"
URL = "http://openapi.alio.go.kr/openapi/service/recruit/list"

def get_job_data(page_no=1, num_rows=10):
    """공공데이터 포털 API에서 채용 데이터를 가져오는 함수"""
    params = {
        'serviceKey': requests.utils.unquote(API_KEY),  # 인코딩 중복 방지
        'pageNo': page_no,
        'numOfRows': num_rows,
    }
    
    try:
        response = requests.get(URL, params=params, timeout=10)
        # 응답 상태 확인
        if response.status_code == 200:
            data_dict = xmltodict.parse(response.text)
            
            # 데이터 구조 확인 및 추출
            body = data_dict.get('response', {}).get('body', {})
            items_obj = body.get('items')
            
            if items_obj and 'item' in items_obj:
                items = items_obj['item']
                # 데이터가 1개일 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]
                return pd.DataFrame(items)
            else:
                return "데이터가 없습니다."
        else:
            return f"API 호출 실패 (상태 코드: {response.status_code})"
            
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 2. UI 레이아웃 설정
st.set_page_config(page_title="공공 채용 알리미", page_icon="💼", layout="wide")

st.title("🏛️ 실시간 공공기관 채용 정보")
st.markdown("---")

# 사이드바 컨트롤러
st.sidebar.header("🔍 검색 및 설정")
page = st.sidebar.number_input("페이지", min_value=1, value=1)
rows = st.sidebar.slider("불러올 공고 수", 5, 50, 10)

if st.sidebar.button("데이터 새로고침"):
    st.cache_data.clear()

# 3. 데이터 로드 및 출력
with st.spinner('최신 채용 정보를 가져오는 중입니다...'):
    df = get_job_data(page, rows)

if isinstance(df, pd.DataFrame):
    # 주요 컬럼 매핑 (API 명세에 따라 필드명은 변경될 수 있습니다)
    # 보통 ALIO API는 'item_nm', 'title', 'work_area' 등을 사용합니다.
    cols_to_show = {
        'item_nm': '기관명',
        'title': '채용 공고명',
        'work_area': '근무지',
        'hire_type': '고용형태',
        'reg_date': '등록일'
    }
    
    # 존재하는 컬럼만 필터링하여 출력
    available_cols = [c for c in cols_to_show.keys() if c in df.columns]
    display_df = df[available_cols].rename(columns=cols_to_show)
    
    st.success(f"현재 {len(df)}개의 공고가 조회되었습니다.")
    st.dataframe(display_df, use_container_width=True)

    # 상세 정보 확인 섹션
    st.subheader("📌 공고 상세 보기")
    selected_title = st.selectbox("상세 정보를 확인할 공고를 선택하세요:", df['title'].unique())
    
    if selected_title:
        detail = df[df['title'] == selected_title].iloc[0]
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**🏢 기관명:** {detail.get('item_nm', '정보 없음')}")
            st.write(f"**📍 근무 지역:** {detail.get('work_area', '정보 없음')}")
        
        with col2:
            st.write(f"**📅 등록일:** {detail.get('reg_date', '정보 없음')}")
            # 실제 공고 링크가 있다면 하이퍼링크 생성
            link = detail.get('src_url', '#')
            st.markdown(f"🔗 [공고 원문 바로가기]({link})")

elif isinstance(df, str):
    st.warning(df)
