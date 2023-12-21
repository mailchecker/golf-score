import streamlit as st
import json
import pandas as pd
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

# 입력 폼 생성
with st.form(key='golfer_form'):
    golfers_data = []
    for i in range(number_of_golfers):
        with st.container():
            name = st.text_input(f'골퍼 {i+1} 이름', key=f'name_{i}')
            stroke = st.number_input(f'스트로크 {i+1}', min_value=0, key=f'stroke_{i}')
            handicap = st.number_input(f'핸디캡 {i+1}', min_value=0, key=f'handicap_{i}')

            # 최종결과 자동 계산
            result = stroke - handicap
            golfers_data.append({'name': name, 'stroke': stroke, 'handicap': handicap, 'result': result})

            # 최종결과 표시
            st.text(f'골퍼 {i+1} 최종결과: {result}')
    
    submit_button = st.form_submit_button(label='저장')

# 날짜 입력 추가
date = st.date_input("날짜")

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
