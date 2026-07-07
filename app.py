import streamlit as st
import pandas as pd
import requests
import numpy as np
import pydeck as pdk
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 스마트 항공 관제탑",
    page_icon="✈️",
    layout="wide"
)

# 큰 제목 설정
st.title("🚨 AI 스마트 항공 관제탑 (한반도 상공)")
st.caption("OpenSky Live API 기반 실시간 한반도 공역 데이터 및 pydeck 3D 입체 관제 시스템")

# 1. 화면 우측 상단에 '수동 새로고침' 버튼 배치
top_col1, top_col2 = st.columns([9, 1])
with top_col2:
    refresh_button = st.button("🔄 수동 새로고침", use_container_width=True)
    if refresh_button:
        st.cache_data.clear() # 캐시를 비워 새로운 데이터를 강제로 가져옴
        st.rerun()

# 2. OpenSky API 실시간 데이터 수집 함수
@st.cache_data(ttl=5)
def get_opensky_data():
    # 한반도 상공 바운딩 박스 (위도 33~39, 경도 124~132)
    lamin, lamax = 33.0, 39.0
    lomin, lomax = 124.0, 132.0
    
    url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lamax={lamax}&lomin={lomin}&lomax={lomax}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            states = json_data.get("states")
            
            if not states:
                return pd.DataFrame()
                
            columns = [
                "icao24", "callsign", "origin_country", "time_position", "last_contact",
                "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
                "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
                "spi", "position_source"
            ]
            df = pd.DataFrame(states, columns=columns)
            
            df["callsign"] = df["callsign"].str.strip()
            df = df[["callsign", "latitude", "longitude", "baro_altitude", "velocity", "vertical_rate"]].dropna(subset=["latitude", "longitude"])
            
            df.columns = ["항공편", "latitude", "longitude", "고도(m)", "속도(m/s)", "vertical_rate"]
            return df
        else:
            st.error(f"OpenSky API 호출 실패 (Status Code: {response.status_code})")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"네트워크 연결 오류: {e}")
        return pd.DataFrame()

# 데이터 로드
flight_df = get_opensky_data()

if not flight_df.empty:
    # Z-score 계산
    vr_series = flight_df["vertical_rate"].fillna(0)
    mean_vr = vr_series.mean()
    std_vr = vr_series.std()
    
    if std_vr == 0 or np.isnan(std_vr):
        flight_df["Z-score"] = 0.0
    else:
        flight_df["Z-score"] = (vr_series - mean_vr) / std_vr

    # 3. 분류 조건 적용: Z-score가 -3 이하인 비행기는 '위험(급강하)', 나머지는 '정상'
    flight_df["상태"] = flight_df["Z-score"].apply(lambda z: "위험(급강하)" if z <= -3.0 else "정상")

    # pydeck 시각화를 위한 색상 정의 (R, G, B)
    flight_df["color"] = flight_df["상태"].apply(lambda s: [255, 75, 75] if s == "위험(급강하)" else [0, 255, 150])

    # 위험 상태 비행기 대수 계산
    danger_count = len(flight_df[flight_df["상태"] == "위험(급강하)"])

    # 4. 화면 중앙에 현재 '위험' 상태인 비행기 수 Metric 표시
    st.markdown("<br>", unsafe_allow_html=True)
    metric_col1, metric_col2, metric_col3 = st.columns([1, 2, 1])
    with metric_col2:
        st.metric(label="⚠️ 현재 공역 내 '위험(급강하)' 항공기 수", value=f"{danger_count} 대")
    
    st.divider()

    # 5. pydeck을 활용한 3D 입체 공역 지도 시각화
    st.subheader("🗺️ 한반도 상공 3D 입체 레이더 맵 (pydeck)")
    
    view_state = pdk.ViewState(
        latitude=36.0,
        longitude=128.0,
        zoom=6.2,
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        flight_df,
        get_position="[longitude, latitude]",
        get_elevation="고도(m)",
        elevation_scale=1,
        radius=3000,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "항공편: {항공편}\n상태: {상태}\n고도: {고도(m)}m\n승강률: {vertical_rate}m/s\nZ-score: {Z-score}"}
    ))

    st.divider()

    # 6. 맨 아래에 전체 비행기 데이터가 담긴 표 배치
    st.subheader("📋 전체 항공 데이터 및 분석 현황")
    display_df = flight_df.rename(columns={"latitude": "위도", "longitude": "경도"}).drop(columns=["color"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("📡 현재 한반도 공역에 탐지된 실시간 OpenSky 항공기 데이터가 없거나 API 호출 제한 상태입니다. 우측 상단의 '수동 새로고침' 버튼을 눌러보세요.")