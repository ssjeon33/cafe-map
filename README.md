# JSS 주경야독 풀캠동선

서울·부천 작업하기 좋은 카페 지도. 현재 위치(GPS) 기준 차량 예상 시간, 도착 후 작업 가능 시간, 마감 뒤 귀가 시각을 보여주고, 버튼 하나로 티맵 길안내를 엽니다.

- 운영: https://ssjeon33.github.io/cafe-map/ (이전 버전: `/v1/`)
- 지도: OpenFreeMap 벡터 타일 © OpenMapTiles, 데이터 © OpenStreetMap contributors (대체: OSM·Esri 이미지 타일 → 자체 지도)
- 지도 엔진: Leaflet 1.9.4 + MapLibre GL JS 4.7.1 (`vendor/`, 라이선스 동봉)
- 도로 경로: OSRM (OpenStreetMap 데이터) + 시간대 혼잡 보정 예상치
- 행정동 경계: vuski/admdongkor
- 빌드: `cd src && python3 build_gh.py` → `src/gh/index.html`을 루트 `index.html`로 복사
