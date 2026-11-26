# Frost Witch V3

V2 몸체, 망토, 기존 텍스처 영역과 다른 본 UUID 유지. 오른쪽 전완 3 unit 단축, hand_right 본 추가, 그립을 1.5 unit 바깥으로 이동. C형 손바닥/손가락/엄지 구조. 지팡이 상·하부 서리 룬, 금속 고리, 코어 프레임 추가. 기존 공유 UV는 변경하지 않고 새 UV에 배치. 256×256, 1:1.

- 116 cubes, 22 bones, 696 faces, 195 unique UV rectangles, 501 shared faces.
- 6 animations, 238 samples at 20 Hz including keyframes. Grip anchor error 0 in approximate FK. Weapon/body OBB candidate frames 0 (declared hand contact excluded); ground threshold 1 unit, minimum -0.15 unit. Max wrist correction 42 degrees.
- Three existing elongated candidates (two calves and shaft), no cloth high warnings.
- Custom renderer and numeric linear XYZ Euler QA, not Blockbench or ModelEngine runtime. No validation of blend transitions, all-body collisions, or exact engine interpolation. Bright rune colors are not actual emissive.
- New weapon ornament motif and shape are design choices, not exact copies of the reference.
