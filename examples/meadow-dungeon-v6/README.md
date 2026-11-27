# Verdant Hollow / V6 — Meadow Dungeon I

Five editable BBMODEL files with embedded textures and 29 unchanged animation tracks/clips (relative to V5). Per-face UVs remain at 1 texel per model unit, with compatible island reuse and 1 px padding. Separate PNGs, four-view previews, walk/attack GIFs, model-specific surface and attachment policies, before/after comparisons for boar/stag/guardian, and machine-readable audit reports are included.

## Changes
- Boar: six separated, stepped dorsal plates instead of eight overlapping sloped plates; front two thorns removed for ear clearance, one thorn replaced by the flower. Re-seat remaining thorns. Bake shoulder moss into hide.
- Stag: preserve dorsal moss and flowers but redesign their support plates; keep omitted flank leaf plates omitted. Lower chest gem into the chest, separate its visible front from the socket.
- Guardian: bake shallow shoulder and shin moss into the supports; retain flower and right-arm attack; refine core and knuckle textures. 
- Moth/slime: retain silhouettes; repaint thin wing/leaf/petal edges. Across the pack, native-sized UVs are repacked and focal textures include edge/cross-section shading instead of blank color strips.

## Verification and limitations
All UV errors, same-facing coplanar/near-parallel candidates, configured protected-face penetration candidates, selected detail-face heuristic warnings and specified attachment-gap warnings are zero at the configured sampling thresholds. 1,249 rest/animation samples, 20 Hz plus keyframes. Unchanged animation arrays confirmed for all five models. The penetration checker inspects every textured face at rest and ONLY policy-selected protected faces during animation; intentional contacts and other rest coverage candidates remain in the JSON. Named thorn/flower roots are exempt on their designated supporting surfaces; side/back portions of gems may be embedded in their sockets. No visibility/alpha-mask/continuous-time or whole-body collision proof. 41 selected attachments checked (not every cube); no attachment policies on moth or slime. Visual review uses a custom software renderer, not Blockbench or ModelEngine. No guarantee of all runtime clipping or Z-fighting being eliminated. No MythicMobs skill configs or emissive effects included.
