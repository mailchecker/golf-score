import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
from datetime import datetime

# Supabase 연결 초기화
conn = st.connection("supabase", type=SupabaseConnection)

# Perform query.
#rows = conn.query("*", table="mytable", ttl="10m").execute()


def test_read_data():
    rows = conn.query("*", table="golf_scores", ttl="10m").execute()
    return rows
    
# Print results.
rows = test_read_data()
for row in rows.data:
    st.write(f"{row['name']} has a :{row['result']}:")


def read_data1(selected_date=None):
    try:
        query = conn.query("*", table="golf_scores", ttl="10m")
        if selected_date:
            # selected_date를 문자열 형식으로 변환
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            # 특정 날짜에 해당하는 데이터만 필터링
            query = query.eq("date", selected_date_str)

        query = query.order("result",desc=True)
        data = query.execute()
        return data
    except Exception as e:
        st.error(f"데이터 불러오기 오류: {e}")
        return []


# 데이터베이스에서 데이터 읽기
def read_data(selected_date=None):
    try:

        if selected_date:
            selected_date_str = selected_date.strftime("%Y-%m-%d")
            query = conn.query("*", table='golf_scores', ttl='0').eq("date",selected_date_str).order("result",desc=True).execute()
        else:
            query = conn.query("*", table='golf_scores', ttl='0').order("result",desc=True).execute()

        return query
    except Exception as e:
        st.error(f"데이터 불러오기 오류: {e}")
        return []


# 데이터베이스에 데이터 쓰기
def write_data(golfer_data):
    try:
        query = conn.query("INSERT INTO golf_scores", golfer_data)
        conn.execute(query)
    except Exception as e:
        st.error(f"데이터 쓰기 오류: {e}")

# 데이터베이스에서 데이터 삭제
def delete_data(date, name):
    try:
        query = conn.query("DELETE FROM golf_scores WHERE date = %s AND name = %s", (date, name))
        conn.execute(query)
    except Exception as e:
        st.error(f"데이터 삭제 오류: {e}")

# 애플리케이션 헤더
st.title('골프 스코어 관리 시스템')

# 골퍼 수 선택
number_of_golfers = st.selectbox('골퍼 수 선택', range(1, 11))

# 날짜 입력 추가
date = st.date_input("날짜")

# 골퍼별 입력칸 배열
golfers_data = []
for i in range(number_of_golfers):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(f'골퍼 {i+1} 이름', key=f'name_{i}')
    with col2:
        stroke = st.number_input('스트로크', min_value=-100, max_value=100, key=f'stroke_{i}')
    with col3:
        handicap = st.number_input('핸디캡', min_value=-100.0, max_value=100.0, key=f'handicap_{i}')
    with col4:
        result = stroke - handicap
        st.number_input('최종결과', value=result, key=f'result_{i}', disabled=True)

    golfers_data.append({'date': date, 'name': name, 'stroke': stroke, 'handicap': handicap, 'result': result})

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
    displayed_data = read_data1(selected_date)
    if displayed_data.data:
        df = pd.DataFrame(displayed_data.data)
        df_sorted = df.sort_values(by='result')
        st.table(df_sorted)
    else:
        st.write("선택된 날짜에 골퍼 정보가 없습니다.")

