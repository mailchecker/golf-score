import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# JSON 파일 읽기 함수
def read_json(filename):
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"파일을 읽는 중 오류 발생: {e}")
        return {}

# JSON 파일 쓰기 함수
def write_json(filename, data):
    try:
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        st.error(f"파일을 쓰는 중 오류 발생: {e}")

# JSON 파일 삭제 버튼
def delete_json(filename):
    try:
        os.remove(filename)
        st.success("JSON 파일이 삭제되었습니다.")
    except FileNotFoundError:
        st.error("파일이 존재하지 않아 삭제할 수 없습니다.")
    except Exception as e:
        st.error(f"파일 삭제 중 오류 발생: {e}")


# 애플리케이션 헤더
st.title('스코어 관리 시스템')

# 데이터 파일 로드 (혹은 초기화)
data = read_json("golfers_data.json")

# 데이터 파일 삭제 (혹은 초기화)
if st.button('JSON 파일 삭제'):
    delete_json("golfers_data.json")



# 골퍼 수 선택
number_of_golfers = st.selectbox('골퍼 수 선택', range(1, 11))

# 입력값 변경시 호출될 함수
def update_result(index):
    stroke_key = f'stroke_{index}'
    handicap_key = f'handicap_{index}'
    result_key = f'result_{index}'

    # 최종 결과 계산 및 저장
    stroke = st.session_state.get(stroke_key, 0)
    handicap = st.session_state.get(handicap_key, 0)
    st.session_state[result_key] = stroke - handicap



# 골퍼별 입력칸 배열
golfers_data = []
for i in range(number_of_golfers):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(f'골퍼 {i+1} 이름', key=f'name_{i}')
    with col2:
        stroke = st.number_input(f'스트로크', min_value=-100, value=0, key=f'stroke_{i}', on_change=update_result, args=(i,))
    with col3:
        handicap = st.number_input(f'핸디캡', min_value=-100, value=0, key=f'handicap_{i}', on_change=update_result, args=(i,))
    with col4:
        # '최종결과' 입력칸을 숫자 형식으로 변경
        result = st.session_state.get(f'result_{i}', 0)
        st.number_input('최종결과', value=result, key=f'result_{i}', disabled=True, min_value=-200)

    golfers_data.append({'name': name, 'stroke': stroke, 'handicap': handicap, 'result': result})

# 날짜 입력 추가
date = st.date_input("날짜")

# 저장 버튼
submit_button = st.button('저장')

# 저장 버튼 클릭시 데이터 처리
if submit_button:
    # JSON 파일 읽기
    data = read_json("golfers_data.json")

    # 날짜 문자열 포맷팅
    date_str = date.strftime("%Y-%m-%d")

    # 해당 날짜에 데이터가 없으면 새로운 리스트 생성, 있으면 기존 데이터에 추가
    if date_str not in data:
        data[date_str] = []

    # 입력된 골퍼 정보 추가
    st.write('------golfers_data-----')
    st.write(golfers_data)
    
    for golfer in golfers_data:
        st.write('------golfer-----')
        st.write(golfer)
        st.write('------data[date_str]-----')
        st.write(data[date_str])
        
        if golfer['name']:  # 골퍼 이름이 비어있지 않은 경우에만 추가
            data[date_str].append(golfer)

    # JSON 파일 쓰기
    write_json("golfers_data.json", data)
    st.success("골퍼 정보가 저장되었습니다.")


# 날짜별 데이터 조회 및 처리
selected_date = st.selectbox("조회할 날짜 선택", options=list(data.keys()))

if selected_date:
    if selected_date in data and data[selected_date]:
        selected_data = list(data[selected_date].values())
        df = pd.DataFrame(selected_data)
        df = df.sort_values(by='result') if not df.empty else df
        st.table(df)

        # 골퍼 삭제 기능
        golfer_names = df['name'].tolist()
        delete_golfer_name = st.selectbox("삭제할 골퍼 선택", options=golfer_names)
        if st.button("골퍼 삭제"):
            df = df[df['name'] != delete_golfer_name]
            data[selected_date] = df.to_dict('records')
            write_json("golfers_data.json", data)
            st.experimental_rerun()
    else:
        st.write("선택된 날짜에 골퍼 정보가 없습니다.")
        # 새 데이터 추가 로직
        if st.button("새 골퍼 정보 추가"):
            data[selected_date] = golfers_data
            write_json("golfers_data.json", data)
            st.experimental_rerun()
            





