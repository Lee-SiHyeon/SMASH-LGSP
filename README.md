# SMASH LGSP — LG사이언스파크 부수기

정신나간 직장인의 회사 부수기 #1. 마곡 LG사이언스파크를 3D로 부수는 브라우저 게임입니다. 회사와 관계없는 비공식 패러디입니다.

**바로 하기:** https://lee-sihyeon.github.io/SMASH-LGSP/

## 도구 (숫자 키 1~6)
1. 사직서 폭탄 — 넓게 날리고 구덩이를 팝니다
2. 결재판 풀스윙 — 크기 ×0.5~×3, 70 m 넘게 날리면 홈런
3. 엑셀 레이저 — 끌어서 선을 그으면 빔이 훑습니다
4. 성과급 운석 — 큰 구덩이
5. 월요병 지진 — 규모 4~10, 7.5 이상이면 건물이 통째로 주저앉습니다
6. 퇴사 핵폭탄 — 반경 420 m

점수는 직급(인턴 → 퇴사각)으로 올라가고, 도구를 바꿔 가며 부수면 배율이 붙습니다. 계속 파면 지구 중심까지 내려갑니다. N 키는 밤 모드입니다.

## 만든 방법
- 엔진은 처음부터 새로 쓴 코드입니다 (`src/main.js`, three.js r160). 건물은 맞는 순간에만 블록으로 쪼개고, 블록·조각·잔해는 InstancedMesh로 몇 번의 드로우콜에 그립니다.
- 느려지지 않게: 날아다니는 조각 수 상한, 멈춘 조각은 계산 없는 잔해로 전환, 그림자는 움직임이 있을 때만 다시 그리기, 프레임이 느리면 해상도 자동 하향.
- 데이터: `python3 tools/build_data.py raw/map.osm config.json data/scene.json` (OSM API `map?bbox=`로 받은 XML)
- 빌드: `npm i && python3 tools/assemble.py` → `dist/index.html` 한 파일. 배포본은 `docs/`.
- 다른 회사: `config.json`의 `bbox`, `siteWays`(OSM 부지 way ID), 이름만 바꾸면 됩니다.

## 출처
지도·건물: © OpenStreetMap 기여자 (ODbL). `data/scene.json`도 ODbL을 따릅니다.
