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
    iframe {margin-bottom: -40px !important;}
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
    st.markdown("#### 💐 메시지 지도")
    if "lat" in df.columns and "lon" in df.columns and not df.empty:
        map_center = [df["lat"].mean(), df["lon"].mean()]
    else:
        map_center = [37.5665, 126.9780]  # 서울 시청 좌표
    m = folium.Map(location=map_center, zoom_start=6)

    for _, row in df.iterrows():
        color = "blue" if row["level"] == "재학생" else (
                "green" if row["level"] == "휴학생" else "red")
        popup_text = f"<div style='font-size: 13px'>{row['name']} ({row['level']}):<br>{row['message']}</div>"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(m, width=750, height=460)

# === 차트 & 워드클라우드 ===
with col2:
    st.markdown("#### 📊 참여자 구성")
    level_counts = df["level"].value_counts()
    colors = {"재학생": "blue", "휴학생": "green", "졸업생": "red"}
    bar_colors = [colors.get(lv, "gray") for lv in level_counts.index]

    fig1, ax1 = plt.subplots(figsize=(4, 1.8))
    ax1.bar(level_counts.index, level_counts.values, color=bar_colors)
    ax1.set_ylabel("메시지 수")
    ax1.set_yticks(range(1, max(level_counts.values)+1))
    ax1.set_title("참여자 구성")
    st.pyplot(fig1)

    st.markdown("#### ☁️ 메시지 워드클라우드")
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
