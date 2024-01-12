import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os


st.write("DB username:", st.secrets["DB_USERNAME"])
st.write("DB_TOKEN:", st.secrets["DB_TOKEN"])
st.write("some_section:", st.secrets["some_section"]["some_key"])
st.write(
    "Has environment variables been set:",
    os.environ["db_username"] == st.secrets["db_username"],
)


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
st.title('골프 스코어 관리 시스템')

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
        stroke = st.number_input('스트로크', min_value=-100, max_value=100, value=0, step=1, format="%i", key=f'stroke_{i}', on_change=update_result, args=(i,))
    with col3:
        # 핸디캡에 소수점 입력을 위한 설정 변경
        handicap = st.number_input('핸디캡', min_value=-100.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", key=f'handicap_{i}', on_change=update_result, args=(i,))
    with col4:
        result = st.session_state.get(f'result_{i}', 0)
        st.number_input('최종결과', value=result, key=f'result_{i}', disabled=True)

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

    # 해당 날짜에 데이터가 없으면 새로운 리스트 생성
    if date_str not in data:
        data[date_str] = []

    # 입력된 골퍼 정보 업데이트 또는 추가
    for golfer_input in golfers_data:
        found = False
        for golfer in data[date_str]:
            if golfer['name'] == golfer_input['name']:
                # 동일한 이름의 골퍼 정보를 업데이트
                golfer.update(golfer_input)
                found = True
                break
        if not found and golfer_input['name']:
            # 새 골퍼 정보 추가
            data[date_str].append(golfer_input)

    # JSON 파일 쓰기
    write_json("golfers_data.json", data)
    st.success("골퍼 정보가 저장되었습니다.")


# 날짜별 데이터 조회 및 처리
#selected_date = st.selectbox("조회할 날짜 선택", options=list(data.keys()))

# 오늘 날짜 문자열 포맷팅
today_str = datetime.now().strftime("%Y-%m-%d")

# 날짜 선택 목록 생성
date_options = list(data.keys())

# 오늘 날짜의 인덱스 찾기
default_index = date_options.index(today_str) if today_str in date_options else 0

# 날짜 선택 위젯에 기본값으로 오늘 날짜 설정
selected_date = st.selectbox("조회할 날짜 선택", options=date_options, index=default_index)

#if selected_date in data:
#    st.write("데이터 타입:", type(data[selected_date]))
#    st.write("데이터 내용:", data[selected_date])
#    try:
#        values = data[selected_date].values()
#        st.write(values)
#    except AttributeError as e:
#        st.error(f"오류 발생: {e}")

if selected_date in data:
    selected_data = data[selected_date]  # '.values()' 호출 제거
    df = pd.DataFrame(selected_data)
    df = df.sort_values(by='result') if not df.empty else df
    st.table(df)

    # 골퍼 삭제 기능
    if not df.empty:
        delete_golfer_name = st.selectbox("삭제할 골퍼 선택", df['name'])
        if st.button("골퍼 삭제"):
            # 선택된 골퍼 이름에 해당하는 데이터를 삭제
            data[selected_date] = [golfer for golfer in selected_data if golfer['name'] != delete_golfer_name]
            write_json("golfers_data.json", data)
            st.experimental_rerun()
else:
    st.write("선택된 날짜에 골퍼 정보가 없습니다.")
    


# 데이터 파일 삭제 (혹은 초기화)
#if st.button('전체초기화'):
#    delete_json("golfers_data.json")



