# Animation and QA
- 대기, 이동, 시전, 공격의 목적 및 방향을 설계한다. 예비 동작 → 가속/타격 또는 시전 → 후속 동작 → 복귀. 지면 접촉과 무기의 양쪽 끝, 얼굴, 팔꿈치, 망토 간섭을 함께 확인한다.
- 최소 20 Hz 시간 샘플링(키프레임 시점 추가)으로 로컬·부모 변환을 누적하여 그립점, 무기 축, 손목 각도, 지면 침범, 무기와 신체/의복 OBB 충돌 후보를 평가한다. 후보는 허용 접촉과 실제 관통을 구분한다. 키프레임 사이의 급격한 각도 변화를 검토한다.
- `scripts/check_weapon_grip.py MODEL --config CONFIG --output REPORT`를 사용한다. config에는 hand_bone, weapon_bone, grip(모델 rest 좌표), optional hand_anchor, weapon_axis, ground_y를 지정한다. 이름과 점은 실제 모델에 맞춰 명시한다. 의도적 죽음/낙하 등은 사유를 따로 기록한다.
- 이 검사기는 숫자 기반 linear keyframe, 기본 scale=1, XYZ Euler 근사 렌더 규약에 한정된다. 표현식/Molang, Bezier/Catmullrom, scale, 다른 회전 순서 등 미지원은 실패로 보고한다. Blockbench/ModelEngine 런타임의 정확한 검증으로 간주하지 않는다.
- 정면/측면/사선 주요 자세와 중간 프레임을 실제 모델에서 렌더한다. 심한 손목 꺾임·신체/천 관통·그립 이탈·지면 침범을 발견하면 자세를 수정하고 재검사한다. 단순 수치 통과로 미술적 자연스러움을 보장하지 않는다. 실제 엔진 테스트 불가 시 명시한다.
