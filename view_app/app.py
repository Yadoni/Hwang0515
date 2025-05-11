import streamlit as st
import gspread
import pandas as pd
import folium
from streamlit_folium import st_folium
from oauth2client.service_account import ServiceAccountCredentials
from wordcloud import WordCloud
from branca.element import Template, MacroElement
import matplotlib.pyplot as plt

# === 인증 설정 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key("1GzHvQUcgFqlUnyBOT2udLcHjslFjsMazlGPIUIDGG14").sheet1

# === UI 초기화 ===
st.set_page_config(page_title="메시지 시각화", layout="wide")
st.title("🗺️ 실시간 메시지 시각화 대시보드")

# === 데이터 로딩 ===
records = sheet.get_all_records()
df = pd.DataFrame(records)

# === 레이아웃 구성 ===
col1, col2 = st.columns([2, 1])

# === 지도 시각화 ===
with col1:
    st.markdown("#### 📍 메시지 위치 지도")
    map_center = [df["lat"].mean(), df["lon"].mean()]
    m = folium.Map(location=map_center, zoom_start=6)

    for _, row in df.iterrows():
        color = "blue" if row["level"] == "재학생" else ("green" if row["level"] == "휴학생" else "red")
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"{row['name']} ({row['level']}): {row['message']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # 레전드 추가
    legend_html = """
    {% macro html() %}
    <div style="position: fixed; bottom: 50px; left: 50px; width: 150px;
                height: 110px; background-color: white; border:2px solid grey;
                z-index:9999; font-size:14px; padding: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
    <b>🟢 level 안내</b><br>
    <svg width="10" height="10"><circle cx="5" cy="5" r="5" fill="blue"/></svg> 재학생<br>
    <svg width="10" height="10"><circle cx="5" cy="5" r="5" fill="red"/></svg> 졸업생<br>
    <svg width="10" height="10"><circle cx="5" cy="5" r="5" fill="green"/></svg> 휴학생
    </div>
    {% endmacro %}
    """
    legend = MacroElement()
    legend._template = Template(legend_html)
    m.get_root().add_child(legend)
    st_folium(m, width=700, height=500)

# === 차트 & 워드클라우드 ===
with col2:
    st.markdown("#### 📊 신분별 메시지 수")
    st.bar_chart(df["level"].value_counts())

    st.markdown("#### ☁️ 메시지 워드클라우드")
    if not df["message"].empty:
        text = " ".join(df["message"].astype(str))
        wc = WordCloud(
            font_path="NanumGothic.ttf",
            background_color="white",
            width=400,
            height=250
        ).generate(text)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("메시지가 아직 없습니다.")
