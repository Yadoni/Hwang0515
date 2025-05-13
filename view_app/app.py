import streamlit as st
import gspread
import pandas as pd
import folium
from streamlit_folium import st_folium
from oauth2client.service_account import ServiceAccountCredentials
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# === 인증 설정 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key("1GzHvQUcgFqlUnyBOT2udLcHjslFjsMazlGPIUIDGG14").sheet1

# === UI 초기화 ===
st.set_page_config(page_title="메시지 시각화", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"]  {background-color: white !important;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    iframe {margin-bottom: -60px !important; display: block;}
    .element-container:has(> iframe) {margin-bottom: -50px !important;}
    </style>
""", unsafe_allow_html=True)

st.title("💐 스승의 날 메시지 시각화 대시보드")

# === 데이터 로딩 ===
records = sheet.get_all_records()
df = pd.DataFrame(records)

# === 한글 폰트 설정 ===
font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rc("font", family="NanumGothic")
else:
    st.warning("한글 폰트 파일 NanumGothic.ttf 이 누락되었습니다. 워드클라우드가 깨질 수 있습니다.")

# === 레이아웃 구성 ===
col1, col2 = st.columns([2.3, 1.2], gap="small")

# === 지도 시각화 ===
with col1:
    st.markdown("#### 📍 감사인사 지도")
    if "lat" in df.columns and "lon" in df.columns and not df.empty:
        map_center = [36.973298, 131.458892]
    else:
        map_center = [36.973298, 131.458892]  # 서울 시청 좌표
    m = folium.Map(location=map_center, zoom_start=6)

    # 사 워드클라우드")
    if not df["message"].empty:
        text = " ".join(df["message"].astype(str))
        wc = WordCloud(
            font_path=font_path if os.path.exists(font_path) else None,
            background_color="white",
            width=400,
            height=200,
            colormap="Set1"
        ).generate(text)

        fig2, ax2 = plt.subplots(figsize=(4, 2.2))
        ax2.imshow(wc, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2)
    else:
        st.info("메시지가 아직 없습니다.")
