# 메시지 전용 입력 앱 (app_input.py)

import streamlit as st
from streamlit_javascript import st_javascript
import gspread
import random
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# === 인증 설정 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key("1GzHvQUcgFqlUnyBOT2udLcHjslFjsMazlGPIUIDGG14").sheet1

# === UI 초기화 ===
st.set_page_config(page_title="메시지 입력", layout="centered")
st.title("📨 황승식 교수님께 감사 메시지 남기기")

# === 위치 수집 시도 ===
st.info("📍 브라우저 위치 권한을 요청합니다. 허용하지 않아도 메시지 저장은 가능합니다.")
coords = st_javascript("navigator.geolocation.getCurrentPosition((pos) => pos.coords);")

# === 위치 처리 ===
if isinstance(coords, dict) and coords.get("latitude") is not None:
    lat = coords["latitude"]
    lon = coords["longitude"]
    st.success(f"📌 위치 확인됨: {lat:.4f}, {lon:.4f}")
else:
    sea_areas = {
        "남해": {"lat": (33.0, 34.5), "lon": (126.0, 129.5)},
        "동해": {"lat": (36.0, 38.5), "lon": (129.5, 131.5)},
        "서해": {"lat": (34.5, 37.5), "lon": (124.5, 126.5)}
    }
    selected_sea = random.choice(list(sea_areas.keys()))
    sea = sea_areas[selected_sea]
    lat = round(random.uniform(*sea["lat"]), 6)
    lon = round(random.uniform(*sea["lon"]), 6)
    st.warning(f"🌊 위치 정보를 사용할 수 없습니다. {selected_sea} 바다 위 무작위 좌표가 사용됩니다: {lat}, {lon}")

# === 메시지 입력 폼 ===
with st.form("message_form"):
    name = st.text_input("이름 (익명 가능)", "")
    level = st.selectbox("신분", ["재학생", "졸업생", "휴학생"])
    message = st.text_area("메시지를 작성해 주세요 (100자 이내)", max_chars=100)
    submitted = st.form_submit_button("메시지 보내기")

if submitted:
    if message.strip() == "":
        st.warning("메시지를 입력해 주세요.")
    else:
        row = [datetime.now().strftime("%Y-%m-%d"), name if name else "익명", level, message, lat, lon]
        sheet.append_row(row)
        st.success("메시지가 구글 시트에 저장되었습니다. 감사합니다 💐")

# === 결과 보기 버튼 ===
st.markdown("---")
st.markdown("👉 메시지 결과가 궁금하다면 아래 버튼을 눌러주세요.")
if st.button("📊 결과 보기 바로가기"):
    st.markdown(
        \"\"\"\n        <meta http-equiv=\"refresh\" content=\"0; url='https://hwang0515-view.streamlit.app'\" />\n        \"\"\", unsafe_allow_html=True
    )

