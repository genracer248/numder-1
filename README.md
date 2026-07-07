# numder-1
# 🚨 AI 스마트 항공 관제탑 (한반도 상공 실시간 관제 시스템)

OpenSky Network의 실시간 항공 데이터 API를 연동하여 한반도 공역 내 항공기들의 위치를 3D로 시각화하고, 통계적 이상치(Z-score)를 기반으로 위험 항공기(급강하)를 실시간으로 탐지하는 Streamlit 기반 웹 애플리케이션입니다.

## ✨ 주요 기능
* **실시간 데이터 연동:** OpenSky API를 통해 한반도 상공(위도 33~39, 경도 124~132)의 실제 항공기 데이터를 5초 주기로 수집
* **3D 입체 레이더 맵:** `pydeck`을 활용하여 항공기의 위도, 경도뿐만 아니라 실제 고도(m)를 3D 기둥 형태로 공역 시각화
* **AI 통계치 기반 이상 탐지:** 수직 승강률(`vertical_rate`)의 평균과 표준편차를 활용해 실시간 **Z-score** 산출
* **긴급 경보 시스템:** Z-score가 `-3` 이하인 통계적 극단치 항공기를 `위험(급강하)` 상태로 자동 분류 및 상단 대시보드에 실시간 카운팅 고지
* **수동 새로고침:** API 호출 제한을 고려한 안정적인 수동 데이터 갱신 기능 제공

## 🛠️ 기술 스택
* **Frontend/Backend:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Data Visualization:** Pydeck (3D Map)
* **API Endpoints:** Requests (OpenSky Network Live API)

## 🚀 로컬 실행 방법

### 1. 필수 라이브러리 설치
프로젝트 실행을 위해 필요한 파이썬 패키지를 설치합니다.
```bash
pip install streamlit pandas numpy pydeck requests
