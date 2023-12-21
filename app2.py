import streamlit as st
import json
from datetime import datetime

# JSON 파일 읽기 함수
def read_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# JSON 파일 쓰기 함수
def write_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# 애플리케이션 헤더
st.title('골퍼 스코어 관리 시스템')

# 데이터 파일 로드 (혹은 초기화)
data = read_json("golfers_data.json")

# 골퍼 수 선택
number_of_golfers = st.selectbox('골퍼 수 선택', range(1, 11))

# 입력값 변경시 호출될 함수
def update_result(index):
    stroke_key = f'stroke_{index}'
    handicap_key = f'handicap_{index}'
    result_key = f'result_{index}'

    # 최종 결과 계산 및 저장
    st.session_state[result_key] = st.session_state.get(stroke_key, 0) - st.session_state.get(handicap_key, 0)


# 골퍼별 입력칸 배열
golfers_data = []
for i in range(number_of_golfers):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(f'골퍼 {i+1} 이름', key=f'name_{i}')
    with col2:
        stroke = st.number_input(f'스트로크', min_value=0, key=f'stroke_{i}', on_change=update_result, args=(i,))
    with col3:
        handicap = st.number_input(f'핸디캡', min_value=0, key=f'handicap_{i}', on_change=update_result, args=(i,))
    with col4:
        # '최종결과'를 문자열로 변환하여 전달
        #result = str(st.session_state.get(f'result_{i}', 0))
        #st.text_input('최종결과', value=result, key=f'result_{i}', disabled=True)

    golfers_data.append({'name': name, 'stroke': stroke, 'handicap': handicap, 'result': result})

# 날짜 입력 추가
date = st.date_input("날짜")

# 저장 버튼
submit_button = st.button('저장')

# 저장 버튼 눌렀을 때의 처리
if submit_button:
    # JSON 파일 읽기
    data = read_json("golfers_data.json")

    # 현재 날짜의 데이터 저장
    date_str = date.strftime("%Y-%m-%d")
    if date_str not in data:
        data[date_str] = []
    data[date_str].extend(golfers_data)

    # JSON 파일 쓰기
    write_json("golfers_data.json", data)

# 날짜별 데이터 조회
selected_date = st.selectbox("조회할 날짜 선택", options=list(data.keys()))
if selected_date:
    selected_data = data[selected_date]
    # 데이터를 최종 결과에 따라 정렬
    sorted_data = sorted(selected_data, key=lambda x: x['result'])
    # 표시
    for golfer in sorted_data:
        st.write(golfer)
