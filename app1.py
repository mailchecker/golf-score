import streamlit as st
from operator import itemgetter

st.title('Golf Score Ranker')

# 선택한 인원 수 및 성적하위 값을 받아옵니다.
num_players = st.selectbox('인원선택', list(range(1, 11)))
num_bottom = st.selectbox('성적하위', list(range(1, min(num_players + 1, 11))))

# 사용자의 입력 값을 저장할 리스트
players = []

for i in range(num_players):
    col1, col2, col3, col4 = st.columns(4)
    name = col1.text_input(f"Player {i + 1} Name", key=f"name_{i}")
    strokes = col2.number_input("Strokes", value=0, key=f"strokes_{i}")
    handicap = col3.number_input("Handicap", value=0.0, key=f"handicap_{i}")
    net = strokes - handicap
    col4.text(f"Net: {net}")
    players.append({'name': name, 'net': net, 'strokes': strokes, 'handicap': handicap})

if st.button('Sort'):
    players = sorted(players, key=itemgetter('net'))

# 하위 순위의 플레이어들을 출력합니다.
bottom_players = players[-num_bottom:]

st.write('---')
st.write('성적하위:')

for player in bottom_players:
    st.write(f"{player['name']} - Strokes: {player['strokes']}, Handicap: {player['handicap']}, Net: {player['net']}")

if st.button('Reset'):
    st.experimental_rerun()
