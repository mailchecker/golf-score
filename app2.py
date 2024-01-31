import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

conn = init_connection()

def manage_pw():
    mpw = st.secrets["MANAGE_PASSWORE"]
    return mpw

def read_data(selected_date=None):
    try:
        query = conn.table("golf_scores").select("*")
        if selected_date:
            # selected_date를 문자열 형식으로 변환
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            # 특정 날짜에 해당하는 데이터만 필터링
            query = query.eq("action_date", selected_date_str)
        query = query.order("result", desc=True)
        data = query.execute()
        return data
    except Exception as e:
        st.error(f"데이터 불러오기 오류: {e}")
        return []


# 데이터베이스에서 데이터 읽기
def read_data_test(selected_date=None):
    try:
        if selected_date:
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            query = conn.query("*", table='golf_scores', ttl='0').eq("action_date", selected_date_str).order("result",
                                                                                                      desc=True).execute()
        else:
            query = conn.query("*", table='golf_scores', ttl='0').order("result", desc=True).execute()
        return query

    except Exception as e:
        st.error(f"데이터 불러오기 오류: {e}")
        return []

def write_data(golfer_data):
    try:
        # 동일한 날짜와 이름을 가진 데이터가 있는지 확인
        #existing_data = conn.table("golf_scores").select("*").eq("date", golfer_data["date"]).eq("name", golfer_data["name"]).execute()
        existing_data = conn.table("golf_scores").select("*", count="exact").eq("action_date", golfer_data["action_date"]).eq("name", golfer_data["name"]).execute()


        if existing_data.count > 0:
            # 기존 데이터가 있으면 업데이트
            response = conn.table("golf_scores").update(golfer_data).eq("action_date", golfer_data["action_date"]).eq("name", golfer_data["name"]).execute()
        else:
            # 기존 데이터가 없으면 새로 삽입
            response = conn.table("golf_scores").insert([golfer_data]).execute()

        # 데이터 작업 성공 여부 확인
        if not response.data or response.data == []:
            raise Exception("데이터 작업에 실패했습니다.")

        return response.data
    except Exception as e:
        st.error(f"데이터 작업 오류: {e}")

# 데이터베이스에서 데이터 삭제
def delete_data(date, name):
    try:
        response = conn.table("golf_scores").delete().eq("action_date", date).eq("name", name).execute()
        # 데이터 작업 성공 여부 확인
        if not response.data or response.data == []:
            raise Exception("데이터 작업에 실패했습니다.")

        return response.data

    except Exception as e:
        st.error(f"데이터 삭제 오류: {e}")

# 애플리케이션 헤더
st.title('골프스코어 관리 시스템')

# 한 줄에 두 개의 입력칸 배치
col1, col2 = st.columns(2)

# 첫 번째 컬럼에 골퍼 수 선택
with col1:
    number_of_golfers = st.selectbox("골퍼 수 선택", range(1, 20))

# 두 번째 컬럼에 날짜 입력
with col2:
    date = st.date_input("날짜", value=datetime.now().date())
    date_str = date.isoformat()

# 골퍼별 입력칸 배열
golfers_data = []

for i in range(number_of_golfers):

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f'골퍼 {i + 1} 이름', key=f'name_{i}')
    with col2:
        stroke = st.number_input('스트로크', value=72, min_value=-100, max_value=100, key=f'stroke_{i}')
    with col3:
        handicap = st.number_input('핸디캡', value=0.0, min_value=-100.0, max_value=100.0, key=f'handicap_{i}')
    with col4:
        result = stroke - handicap
        st.number_input('최종결과', value=result, key=f'result_{i}', disabled=True)
    with col5:
        # 승패 여부 선택 리스트 박스
        is_winner = st.selectbox('승패 여부', [True, False], key=f'winner_{i}')

    golfers_data.append({'action_date': date_str, 'name': name, 'stroke': stroke, 'handicap': handicap, 'result': result, 'iswinner': is_winner})


# 저장 버튼
submit_button = st.button('저장')

# 저장 버튼 클릭 시 데이터 처리
if submit_button:

    for golfer in golfers_data:
        if golfer['name']:  # 이름이 있는 골퍼만 저장
            write_data(golfer)
    st.success("골퍼 정보가 저장되었습니다.")


# 날짜별 데이터 조회 - 기본값으로 오늘 날짜 사용
today = datetime.now().date()
selected_date = st.date_input("조회할 날짜 선택", value=today)

# 조회된 데이터 표시

if selected_date:
    displayed_data = read_data(selected_date)

    if displayed_data.data:
        df = pd.DataFrame(displayed_data.data)
        # '핸디캡'과 '결과' 컬럼을 소수점 첫째 자리까지 반올림
        df['handicap'] = df['handicap'].round(1)
        df['result'] = df['result'].round(1)

        df = df.sort_values(by='result') if not df.empty else df
        st.table(df)


        # 골퍼 삭제 인터페이스
        if not df.empty:
            delete_golfer_name = st.selectbox("삭제할 골퍼 선택", df['name'])

            # 삭제 버튼
            if st.button("골퍼 삭제"):
                st.session_state['delete_pressed'] = True

            # 삭제 버튼이 눌렸을 때만 비밀번호 입력 상자 표시
            if 'delete_pressed' in st.session_state and st.session_state['delete_pressed']:
                input_password = st.text_input("비밀번호를 입력하세요", type="password", key="delete_password")

                # 비밀번호 확인 후 삭제 작업 진행
                if st.button("삭제 확인"):
                    if input_password == manage_pw():
                        delete_data(selected_date, delete_golfer_name)
                        st.success("골퍼가 성공적으로 삭제되었습니다.")
                        del st.session_state['delete_pressed']  # 상태 초기화
                        st.experimental_rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
        else:
            st.write("선택된 날짜에 골퍼 정보가 없습니다.")


