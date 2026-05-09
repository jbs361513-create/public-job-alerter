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
            # API 응답 구조가 'result' 안에 리스트가 있는지 확인
            items = data.get('result', [])
            
            if items and isinstance(items, list):
                return pd.DataFrame(items)
            else:
                return None # 데이터가 비었을 때
        else:
            return f"API 연결 실패: {response.status_code}"
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 2. UI 레이아웃
st.set_page_config(page_title="공공기관 채용 알리미", layout="wide")
st.title("🏛️ 실시간 공공기관 채용 정보")

# 사이드바
page = st.sidebar.number_input("페이지 번호", min_value=1, value=1)
rows = st.sidebar.slider("조회 개수", 5, 50, 10)

# 3. 데이터 로드
df = get_job_data(page, rows)

# 데이터가 DataFrame 형태이고 비어있지 않은지 확인
if isinstance(df, pd.DataFrame) and not df.empty:
    
    # [중요] 실제 API가 주는 컬럼명을 확인하기 위한 로직
    # 만약 'title'이 없다면 데이터프레임 전체를 보여줘서 확인하게 함
    actual_columns = df.columns.tolist()
    
    # 우리가 기대하는 컬럼명 리스트 (API 명세에 따라 다를 수 있음)
    # 기재부 알리오 API의 실제 키값은 보통 'title', 'instNm' 등입니다.
    target_col = 'title' if 'title' in actual_columns else (actual_columns[0] if actual_columns else None)

    if target_col:
        st.success(f"총 {len(df)}개의 데이터를 불러왔습니다.")
        st.dataframe(df, use_container_width=True)

        st.subheader("📌 공고 상세 정보")
        # KeyError 방지: 'title' 컬럼이 있는지 확실히 체크
        if 'title' in df.columns:
            selected_title = st.selectbox("조회할 공고를 선택하세요:", df['title'].unique())
            detail = df[df['title'] == selected_title].iloc[0]
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**🏢 기관명:** {detail.get('instNm', '정보없음')}")
                st.write(f"**📍 근무지:** {detail.get('regionNm', '정보없음')}")
            with c2:
                st.write(f"**📅 등록일:** {detail.get('regDate', '정보없음')}")
                link = detail.get('srcUrl', '#')
                if link != '#': st.link_button("공고 원문 보기", link)
        else:
            st.warning("데이터에 'title' 항목이 포함되어 있지 않습니다. 컬럼명을 확인해주세요.")
            st.write("사용 가능한 항목들:", actual_columns)
    else:
        st.error("데이터 구조를 분석할 수 없습니다.")

elif df is None:
    st.info("조회된 데이터가 없습니다. 페이지 번호를 조절해 보세요.")
else:
    st.error(df) # 에러 메시지 출력
if isinstance(df, pd.DataFrame) and not df.empty:
    # 인덱스를 1부터 시작하도록 변경
    df.index = df.index + 1 
    
    # ... 이후 출력 로직 ...
