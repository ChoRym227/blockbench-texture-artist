---
name: blockbench-texture-artist
description: Create, revise and validate high-quality pixel-art textures and UV atlases for Blockbench bbmodel Minecraft entities, monsters, bosses and equipment, especially ModelEngine 4. Trigger for reference-image-based editable bbmodel creation, humanoid anatomy, cloak and robe geometry, model revision, texturing, UV mapping or model quality review, weapon design, grip alignment, geometry integrity, Z-fighting prevention, surface penetration, multi-face readability, and animation review; not for unrelated image generation.
---
# Blockbench Texture Artist

## V6 mandatory surface gate
Read `references/surface-penetration.md` and `references/multiface-readability.md` for every model or geometry/texture revision. Retain V5. Define named protected surfaces and supports, design layered geometry with its supporting body, paint all exposed material faces, and inspect oblique/elevated detail renders. Run `check_interpenetration.py`, `check_attachment.py`, `check_multiface_readability.py` plus V5 tools. The first checks all textured faces at rest and configured protected faces during sampled animations; the second checks explicit support contacts, and the third reports selected-face texture heuristics. Never treat missing policies or zero warnings as artistic approval. Document allowed contacts and remaining limits.

## V5 mandatory geometry gate
Before UV or animation release, read `references/geometry-integrity.md` and run `scripts/check_z_fighting.py`. Same-facing coplanar/near-coplanar overlaps must be corrected, not hidden by texture or uniform epsilon shifts. Check transformed cube faces in rest and animated poses (20 Hz plus keyframes), record opposing contacts separately, and rerun UV and hierarchy validation after each geometry change. No clean-runtime claim without runtime tests.

## 기본 환경 및 목표
Minecraft Paper 1.21.4 / ModelEngine 4 / Blockbench. 사용자 지정 환경이 우선한다. 레퍼런스의 실루엣, 색감, 재질과 장식 배치를 보존하고, 실제 편집 가능한 모델과 일관된 픽셀 텍스처를 제작한다. 단일 이미지에 없는 면은 추정임을 명시한다.

## 기본 제작 설정
| 항목 | 기본값 |
|---|---|
| 일반 몬스터 아틀라스 | 64×64 또는 128×128 |
| 대형 몬스터/보스 아틀라스 | 128×128 또는 256×256 |
| 픽셀 밀도 | 모델 1 unit당 1 texel부터 시작; 전체 모델 일관성 유지 |
| 재질별 기본 팔레트 | 4~7색 |
| 필터 및 확대 | Nearest Neighbor |
| UV | Per-face UV 우선, 의도적 공유만 허용 |
| 명암 | Pixel Clustering + 절제된 Baked AO |
| 출력 | RGBA PNG, 불필요한 반투명 픽셀 금지 |
| 절차적 생성 | 고정 seed 기록 |
| 검수 | 정면/후면/측면/사선 렌더링 및 반복 수정 |

아틀라스 크기는 실제 표면적과 UV 패킹 결과로 결정한다. 맞지 않으면 해상도를 올리고, 모델마다 픽셀 밀도를 무조건 변경하지 않는다. 기본값은 권장치이며 사용자가 다른 설정을 지정하면 그 설정을 따른다.

## 작업 절차
1. 입력 이미지와 기존 bbmodel을 확인하고 원본 백업. 실제 모델 포맷/버전, 텍스처 크기, 각 큐브의 from/to, rotation, origin, 면별 UV, 텍스처 참조, 본 구조를 분석한다. 기존 애니메이션은 요청 없이 변경하지 않는다.
2. 신규 모델 또는 형상 수정은 아래 형태 설계 게이트를 먼저 통과한다. 신체 부위 및 각 면에 재질을 할당한다. 색상 램프와 장식 위치를 먼저 결정한다. 참고 이미지의 화면 조명, 그림자, 블룸을 원본 텍스처로 오인하지 않는다.
3. UV 섬 크기를 결정하고 정수 픽셀 좌표로 배치한다. 기존 UV는 가능한 보존한다. 새 아틀라스는 면 크기 및 방향, UV 회전/뒤집힘을 고려하고 여유 공간이 있을 때 1px 이상의 패딩을 둔다. 불필요한 중복은 제거하되 대칭 공유는 의도적으로 사용한다.
4. 재질별 기본색 → 명암 군집 → 표면 패턴 → 모서리/접촉 음영 → 장식/손상 순서로 그린다. 각 얼굴의 픽셀을 개별 독립 난수로 결정하지 않는다. 고정 seed로 큰 군집부터 만들고 작은 군집은 제한한다. 이미지 생성은 사용자가 별도 이미지 또는 텍스처 이미지 생성을 명시한 경우에만 수행한다. bbmodel 제작·스킬 수정 요청을 컨셉 이미지로 대체하지 않는다. UV는 실제 모델 좌표에 맞게 배치한다. Pillow/NumPy나 실제 Blockbench 도구를 사용하고 사용할 수 없는 도구는 실행했다고 주장하지 않는다.
5. PNG를 RGBA로 저장하고 모델에 정확하게 연결한다. 가능한 경우 텍스처 데이터를 bbmodel에 내장하고 외부 PNG도 제공한다. 기존 UUID, outliner, 애니메이션, 기타 메타데이터는 보존한다.
6. 렌더링하여 레퍼런스와 비교하고 수정한다. 실제 Blockbench 또는 ModelEngine 실행이 불가능하면 그 검증이 미실행임을 표시한다. 구조 검사와 실제 시각/런타임 검증을 구분한다.


## 형태 설계 게이트 — 인간형 / 천 / 유기적 형태 (필수)

이 규칙은 신규 모델 제작 및 형상 개선에 적용한다. 텍스처만 수정하는 요청에서는 기존 형상을 무단 변경하지 않고 문제를 보고한다. 목표는 Minecraft 특유의 각진 면을 유지하면서 큐브 나열이 아니라 의도적인 덩어리와 실루엣을 만드는 것이다. 큐브 수나 UV 공유율은 미술 품질의 대체 지표가 아니다.

### 1. 제작 순서: 실루엣 → 덩어리 → 관절 → 표면 → 디테일
- 레퍼런스에서 뿔·무기·망토를 제외한 신체 높이 H, 머리 높이, 어깨폭, 골반폭, 팔꿈치·손목·무릎·발목 위치 및 체중 중심을 먼저 정리한다. 정면과 측면 설계 모두 포함한다. 뿔 높이 또는 무기를 몸통 비례 계산에 넣지 않는다.
- 인간형은 머리, 흉곽, 골반의 독립된 입체 덩어리와 팔·다리의 관절 연결부터 만든다. 단순히 정육면체를 세로로 늘려 장신형을 만들지 않는다. 기본 참고 범위는 일반 인간형 6~8두신, 장신형 7~9두신, 어깨폭 1.8~2.6 머리폭, 팔꿈치 허리 부근, 손목 골반 아래, 무릎 다리 중간 부근이다. Minecraft 스타일·연령·체형·괴물 특성에 맞춰 조정하고 의도적 과장은 기록한다. 인간형 요청을 임의로 비인간형으로 바꾸지 않는다.
- 흉곽에서 허리와 골반으로 이어지는 폭·깊이 변화를 만든다. 팔뚝/종아리는 상완/허벅지와 두께 차를 두고, 관절과 손발을 실제 연결한다. 앞뒤 깊이를 확보하고 정면에서만 좋아 보이는 판자형 몸체를 금지한다. 가면은 전면 장식뿐 아니라 뒤통수·턱·목과 연결한다.
- 회전 큐브의 pivot은 실제 관절에 둔다. 숨겨진 내부 신체는 애니메이션 및 관절 검수에 필요한 만큼만 유지하며 망토·로브 안의 불필요한 중복 geometry를 제거한다. 좌우 대칭은 기본 골격에 활용하되 천과 손상, 무기 자세는 레퍼런스에 맞게 변형한다.
- 주 덩어리(몸·로브·망토), 중간 덩어리(깃·갑옷·소매), 작은 디테일(장식·손상)의 위계를 만든다. 대형 장식을 더해 비례 문제를 가리지 않는다.
- 단색 blockout을 정면/측면/후면/3⁄4로 렌더링하고 실루엣과 관절을 수정한 후에만 UV와 텍스처 작업으로 진행한다. 최종 렌더링에서만 처음 확인하지 않는다.

### 2. 라인 큐브 사용 제한 (anti-line-cube)
- 주름, 옷의 봉제선, 띠, 윤곽선, 균열, 작은 장식선 등을 길고 좁은 큐브로 반복 나열하지 않는다. 대부분 텍스처의 연결된 색면·군집으로 표현한다. 돌출이 실루엣 또는 애니메이션에 실제 기여할 때만 형상화한다.
- 치수를 a≤b≤c로 정렬한다. c≥12 model units이고 c/b≥3이면 장척 검토 대상으로 분류한다. 특히 천에서 c/b≥4는 강한 경고다. 이는 미술 검토용 휴리스틱이며 보편적 엔진 제한이 아니다. 지팡이, 검, 뿔의 일부, 정상적인 팔다리 등 기능상 필요한 형상은 비례와 연결을 확인하고 근거를 기록한다. 정해진 수치만 피하려 큐브를 쪼개는 것은 금지한다.
- 같은 방향의 좁은 장척 부품 세 개 이상이 인접하면 반복 리본/판자 구조인지 검토한다. 망토나 로브의 주요 면이 이러한 부품에 의존하면 재설계한다. 여러 큐브를 잘게 분할하더라도 같은 폭의 직선 사슬을 유지하면 불합격이다.
- 유기적 뿔과 가지는 뿌리의 볼륨 → 방향 전환 → 폭 감소 → 끝의 순서로 설계한다. 접합부의 틈, 돌출된 직각 모서리, 동일 두께의 선분 사슬을 피한다. 허용된 큐브 회전과 짧은 폭 변화로 자연스러운 각진 흐름을 만든다.
- 검수 도구 `scripts/check_geometry.py`를 실행하여 장척 후보를 확인한다. 자동 이름 분류에 의존하지 말고 실제 역할을 확인한다. 수치에 문제가 없어도 렌더가 어색하면 실패다.

### 3. 망토·로브·치마 — 넓은 천 면을 먼저 설계
- 먼저 천의 고정점(목, 어깨, 허리), 중력 방향, 바람 방향, 접촉하는 신체를 정한다. 망토는 어깨에서 등으로 감싸며 폭과 깊이가 변화해야 한다. 로브는 허리/골반에서 아래로 자연스럽게 퍼지며 앞뒤 옆면이 하나의 의복처럼 이어져야 한다.
- 기본 구조는 넓은 안감/본체 1층 + 겹쳐진 넓은 바깥 천 면 1~2층 + 필요한 부분의 끝단이다. 망토 전체를 가늘고 독립적인 기둥 5~10개로 구현하지 않는다. 폭은 부위에 따라 다르게 하고 층별 길이·깊이·회전 방향을 설계한다. 어깨에서 밑단까지 동일 폭·동일 각도·동일 간격을 반복하지 않는다.
- 큐브 기반 엔진에서는 넓은 얇은 판, 폭이 바뀌는 계단식 덩어리, 완만하게 각도가 달라지는 2~4개 안팎의 연결 구간을 출발점으로 사용한다. 정확한 구간 수는 레퍼런스와 동작에 따른다. 끝단의 비대칭·겹침은 의도적으로 배치하고 무작위 회전은 금지한다. 동일 면의 중첩으로 인한 z-fighting과 이음매 구멍을 확인한다.
- 예: 기존 2×5×45 후면 판 다섯 개를 반복하는 대신, 몸폭과 망토폭에 맞는 넓은 상부/중부/하부 판을 우선 설계한다(예시 12×14×1 → 16×14×1 → 20×12×1, X×Y×Z). 실제 연결, 회전, 인접 가장자리 겹침, pivot 및 곡면의 근사 형상을 검증한다. 이 치수는 복사할 프리셋이 아니다.
- 찢어진 끝단과 구멍은 작은 계단형 실루엣 또는 완전 투명(alpha 0) 픽셀의 컷아웃으로 처리한다. 실제 런타임의 알파 처리와 뒷면 표시를 확인한다. 천 전체를 긴 막대로 찢거나, 큰 구멍을 반투명 픽셀로 흐리게 표현하지 않는다. 알파 컷아웃을 쓰면 앞뒤 가시성과 가장자리 UV를 확인한다.
- 망토·로브는 UV 공유보다 연결된 주름 방향과 면별 시각적 연속성이 우선이다. 큰 밝고 어두운 면으로 접힘을 만들고, 반복적인 1px 밝은 세로 테두리·평행 줄무늬·모든 큐브의 외곽선 강조는 금지한다. 주름은 일부가 연결되거나 사라지며 강약과 폭이 달라져야 한다.
- 망토 애니메이션이 요청되면 고정점 본에서 중간/끝 본으로 이어지는 부모-자식 계층을 만들고 지연된 움직임을 적용한다. 천을 움직이는 독립 막대 다발로 만들지 않는다. idle/walk/attack 등의 주요 자세에서 어깨·팔·몸 관통, 빈틈, 과도한 꺾임을 확인한다. 로브 하단은 다리 가동 범위에 맞게 분할한다.

### 4. 제작 환경 제약 및 승인 게이트
- ModelEngine 대상은 지원되는 cube/bone 구조를 우선한다. mesh, 자유 변형 면, 이중면, alpha cutout, 특수 효과는 정확한 대상 버전 지원을 확인하기 전에는 호환된다고 주장하지 않는다. 임의 메시를 큐브 엔진으로 내보낼 수 있다고 가정하지 않는다.
- UV 작업 전 단색/무텍스처 렌더로 (1) 비례 (2) 앞뒤 깊이 (3) 주 덩어리 (4) 천의 연결과 밑단 (5) 라인 큐브 의존성을 검수한다. 불합격하면 색상이나 장식 추가로 덮지 말고 geometry를 수정하고 다시 렌더링한다.
- 최종 단계에서 정면/측면/후면/사선 및 가능한 경우 관절 자세를 실제 산출 모델에서 렌더링한다. 레퍼런스와 실제 모델의 실루엣을 비교한다. 렌더링 불가 시 그 사실을 명시하고 통과했다고 주장하지 않는다. 기존 모델 수정 시 이전/이후 동일 카메라 구도의 비교가 권장된다.
- 원본의 형태를 비인간적으로 바꾸거나 과도하게 장신화하는 것은 사용자 요청 또는 레퍼런스 근거가 있는 경우만 허용한다. 스킬 수정 요청이면 스킬 파일을 산출하고 이미지나 새 모델 생성으로 대신하지 않는다.

## 면별 UV 재사용 및 픽셀 밀도 강제 규칙
- 신규 모델의 모든 면은 큐브의 로컬 from/to 치수로 UV 폭·높이를 산정한다. north/south = X×Y, east/west = Z×Y, up/down = X×Z. 회전된 큐브도 회전 전 로컬 치수를 사용한다. UV 회전 90/270도일 때만 UV 폭·높이의 대응을 교환한다.
- 기본 밀도는 1 unit = 1 texel이다. 모든 면에 동일한 밀도 배율을 적용하고, UV를 임의로 늘리거나 줄이거나 정사각형으로 강제하지 않는다. 소수 치수가 필요하면 공통 밀도/격자를 선택해 정수 UV가 되도록 설계하고, 불가피한 반올림은 명시한다.
- 동일한 면 치수·재질·표면 방향·그림 의도가 일치하면 기존 UV 섬을 재사용한다. 좌우 대칭 부위는 필요한 경우 UV를 뒤집어 재사용하고, 반전되면 안 되는 얼굴·문양·방향성 결·고유 손상은 독립 UV를 사용한다. 크기가 다른 면을 하나의 UV로 억지로 공유하지 않는다.
- UV 패킹 전에 재사용 키(재질, UV 폭, UV 높이, 표면 패턴/방향)를 구성하고, 호환되는 얼굴은 동일한 UV 사각형을 참조한다. 재사용 가능 영역은 적극 공유하되 의도하지 않은 부분 중첩은 금지한다.
- 아틀라스가 부족하면 먼저 중복 제거 및 패킹 최적화를 수행하고, 그래도 부족하면 아틀라스 해상도를 늘린다. 개별 면의 UV만 축소하여 공간을 확보하지 않는다. 가능하면 섬 둘레에 1px 패딩 또는 가장자리 색상 확장(extrusion)을 둔다.
- 완료 검수에 각 면의 UV 폭/높이 대 실제 큐브 면 치수, 공통 texel 밀도, 고유 UV 수/전체 면 수, 공유 중첩의 적합성, 범위/텍스처 참조를 자동 검사하고 결과를 기록한다.

## 미술 규칙
- 큰 색면과 연결된 픽셀 군집을 우선한다. 무의미한 소금후추 노이즈, 무차별 디더링, 흐릿한 그라데이션, 과도한 외곽선을 피한다.
- 밝기 변화에 따른 제한적인 hue shifting을 사용한다. 색상을 단순 RGB 가감으로만 생성하지 않는다.
- 석재: 불규칙한 각진 군집, 깊은 균열의 암색과 선택적인 밝은 가장자리. 전체 표면에 균열을 반복하지 않는다.
- 이끼: 윗면과 홈 위주, 면 경계를 넘어 이어지는 불규칙한 덩어리. 밝은 잎과 어두운 밑층을 구분한다.
- 수정: 면별 색면, 밝은 중심/모서리 및 어두운 측면. 마법 룬은 읽히는 실루엣을 우선한다. 실제 emissive는 대상 엔진이 지원하는 방식이 확인된 경우만 설정한다. PNG 자체의 밝은 색은 발광을 보장하지 않는다.
- 금속: 선택적 날카로운 하이라이트, 가죽/천: 낮은 대비의 결 및 주름, 목재: 방향성 결, 뼈: 밝은 면과 접합부 음영.
- 방향에 따른 명암은 약하게 적용하고 게임 조명과 중복되지 않도록 한다. 접촉 음영은 관절/홈/겹치는 부위에 국소적으로 사용한다.
- 기본 불투명 재질은 alpha 255, 빈 공간은 alpha 0. 의도된 투명 효과는 예외로 명시한다. 색상 양자화는 재질 단위로 하고 Nearest Neighbor 확대를 사용한다.

## 룬 골렘 프리셋 (예시)
레퍼런스가 보라색 석재와 청록 수정의 룬 골렘일 때만 우선 사용한다. 원본에서 추출한 정확한 팔레트는 아니다.
- 석재: #252438 #35344B #49445F #5E5673 #777087 #938CA1
- 이끼: #14392E #20513B #2F6945 #428050 #62965B #85AF70
- 수정: #164B60 #187B8B #20B5B9 #3AE1DA #91FFF3 #F0FFFF
- 가슴 코어와 눈을 주요 시선 집중점으로 사용하고 어깨 수정과 이끼는 보조 장식으로 둔다.

## 무기 디자인·파지·애니메이션 게이트 (V3)
무기 또는 손에 든 물체가 있는 신규/수정 모델은 아래 문서를 반드시 읽고 적용한다. 해당 범위가 아닌 원본 몸체와 UV, 애니메이션은 보존한다.
- [무기 디자인](references/weapon-design.md): 1차 실루엣, 2차 구조, 3차 문양. 무기 확대 검수와 공유 UV의 오염 방지.
- [파지 및 자세](references/weapon-grip-and-pose.md): 손목/무기 본 분리, 실제 그립점, 무기 종류별 방향, 손가락 접촉 및 부모 회전 보정.
- [애니메이션 검수](references/animation-principles.md): 최소 20Hz 샘플, 그립 이탈, 충돌 후보, 지면·손목 검사 및 중간 프레임 렌더링.
- 무기 수정 후 `scripts/check_uv.py`와 `scripts/check_weapon_grip.py` 실행 결과 및 남은 후보를 기록한다. 검사 통과와 실제 런타임 호환성을 구분한다. 필요한 무기 축은 기존 라인 큐브 규칙의 예외이나 장식선은 예외가 아니다.

## 완료 기준
- 신규/형상 수정 모델은 형태 설계 게이트 및 장척 후보 검토를 통과해야 한다. 비례, 실루엣, 천 연결, 반복 선형 큐브의 사용 근거, 관절 자세 검수 결과를 기록한다.
- UV 경계 및 의도하지 않은 중첩, 텍스처 참조 누락, PNG 크기/알파, 일관된 픽셀 밀도 확인.
- 색상 수는 재질별로 평가하며 전체 아틀라스에 단일 제한을 강요하지 않는다.
- 관절 주변 UV/텍스처 연결 확인, 기존 애니메이션과 본 보존 확인.
- 최종 산출물: 요청된 bbmodel, PNG 아틀라스, 가능한 경우 렌더링 이미지, 사용한 설정/seed와 검증 결과. 실제로 생성한 파일만 제공하고 미검증 항목을 명시한다.


## V3.1 Addendum — Focal Prop Cleanup

### Weapon texture readability
- On focal props such as staffs, lanterns, and relics, separate **frame**, **core**, **glow**, and **brace** materials clearly.
- Avoid large flat white glow columns without a readable frame relationship. The glow chamber should feel embedded, not pasted on.
- Back faces must not simply mirror the front if that creates awkward read; use a dedicated rear-panel design when needed.

### Rear silhouette cleanup
- Do not place a support cube or flat square slab behind a focal prop unless it is clearly justified by the design in front, side, and back views.
- If a detail exists only to make the front look fuller, prefer texture detail or a thinner frame treatment over a protruding rear cube.
- In 3/4 view, check for isolated boxy cubes that break the silhouette of the weapon head.

### Prop review checklist
- Review the weapon in front, 3/4, side, and back views before finalizing.
- Verify that shallow decoration uses texture/UV by default; use cubes only for silhouette-relevant structure.
- If the prop has a glowing core, ensure the front face remains the visual focus and the side/rear faces do not overpower it.


## V4 Combat Motion Gate
Read [Combat stance and choreography](references/combat-stance-and-choreography.md) for every armed humanoid motion task. A zero-collision report alone is not a visual approval. Reference animation access, actual retargeting, and independently authored approximations must be clearly distinguished.


## V5 — Z-fighting 필수 검수
- `references/geometry-integrity.md`를 읽고 신규 제작과 수정에 적용한다. UV 공유와 실제 3D 동일 평면 중첩을 구분한다.
- `python scripts/check_z_fighting.py MODEL --hz 20 --strict-near --output z_fighting_audit.json` 실행. 기본 자세 및 모든 모션의 실제 변환된 면의 중첩 후보를 검사한다. 동일 방향의 동일/근접 평면 면적 중첩은 해결 후 재검사한다. 반대 방향 접촉 및 미지원 기능은 별도로 기록한다.
- 장식 복원 시 원래 부모 본, UUID 및 pivot을 보존하고 UV 크기 검사도 재실행한다. 실제 런타임 확인 불가 시 반드시 명시한다.
