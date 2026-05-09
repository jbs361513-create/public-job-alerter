import streamlit as st
import requests
import pandas as pd

# 1. API 설정
API_KEY = "dc305c4d0abc3cb89807335cb6775032c45c4f2942b70c74b82b705f139aa715"
BASE_URL = "https://apis.data.go.kr/1051000/recruitment/list"

def get_job_data(page_no=1, num_rows=10):
    params = {
        'serviceKey': requests.utils.unquote(API_KEY),
        'pageNo': page_no,
        'numOfRows': num_rows,
        'resultType': 'JSON'
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('result', [])
            if items:
                return pd.DataFrame(items)
        return None
    except:
        return None

# 2. UI 레이아웃
st.set_page_config(page_title="공공기관 채용 알리미", layout="wide")
st.title("🏛️ 실시간 공공기관 채용 정보")

page = st.sidebar.number_input("페이지 번호", min_value=1, value=1)
rows = st.sidebar.slider("조회 개수", 5, 50, 10)

# 3. 데이터 로드 및 처리
df = get_job_data(page, rows)

if df is not None and not df.empty:
    # 인덱스 1부터 시작
    df.index = df.index + 1

    # 📌 핵심 수정: API 실제 키값인 'recrutPbancTtl'을 사용합니다.
    title_key = 'recrutPbancTtl' 
    
    # 상단 요약 표 출력
    cols_to_show = {
        'instNm': '기관명',
        title_key: '채용 공고명', # 실제 키값 매핑
        'workRgnNmLst': '근무지역',
        'pbancEndYmd': '마감일'
    }
    
    available_cols = [c for c in cols_to_show.keys() if c in df.columns]
    display_df = df[available_cols].rename(columns=cols_to_show)
    
    st.success(f"현재 {len(df)}개의 채용 공고가 조회되었습니다.")
    st.dataframe(display_df, use_container_width=True)

    # 상세 정보 섹션
    st.markdown("---")
    st.subheader("📌 공고 상세 보기")
    
    # selectbox에서도 실제 키값 사용
    selected_title = st.selectbox("상세 내용을 확인할 공고를 선택하세요:", df[title_key].unique())
    
    if selected_title:
        detail = df[df[title_key] == selected_title].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**🏢 기관명:** {detail.get('instNm', '정보없음')}")
            st.write(f"**📍 근무지역:** {detail.get('workRgnNmLst', '정보없음')}")
            st.write(f"**💼 채용구분:** {detail.get('recruitSeNm', '정보없음')}")
        
        with col2:
            st.write(f"**📅 모집기간:** {detail.get('pbancBgngYmd')} ~ {detail.get('pbancEndYmd')}")
            st.write(f"**👤 채용인원:** {detail.get('recrutNope', '0')}명")
            
            link = detail.get('srcUrl', '#')
            if link != '#':
                st.link_button("👉 공고 원문 바로가기", link)

else:
    st.warning("데이터를 불러오지 못했습니다. 인증키나 페이지 번호를 확인해주세요.")
