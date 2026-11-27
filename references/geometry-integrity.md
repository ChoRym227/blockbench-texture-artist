# V5 — Geometry integrity and Z-fighting prevention

## Mandatory gates
- Apply before texture painting, after model edits, and again after animation work. UV overlap is not 3D overlap; intentionally reused UV islands are permitted. Do not use only unrotated from/to or AABB intersection to decide that a model is clean.
- In a solid visible surface, each region has one owner. Do not stack same-facing coplanar surfaces with positive overlapping area. Eliminate duplicate cubes; use contiguous edges or change the volume layout. Keep intentional internal structural contact only when documented, hidden throughout motion, and supported by the target renderer.
- For overlaps on both sides of a joint, redesign the joint cross-section with integer dimensions, preserving the pivot and articulation. Do not merely move all parts by the same epsilon. For isolated surface overlaps, move the actual offending part along the relevant normal, keeping support contact, its origin, its dimensions, symmetry and the original hierarchy. For shallow moss, fur, engraving, or paint, use a unique texture island instead of a coplanar overlay. Keep major silhouette details (antlers, blossoms, armor plates) where they contribute. Do not restore flank clutter when only dorsal decorations were requested.
- Use exact epsilon 0.0001 model unit, near review distance 0.10 model unit, normals within 0.1 degrees of parallel, positive projected overlap area > 0.00001 square model units. These are conservative analysis thresholds, NOT universal depth-buffer guarantees. Try 0.15–0.25 model unit for an isolated depth adjustment where appropriate; never shift blindly, and review scale-down/squash at its smallest scale. Preserve integer face dimensions whenever possible; when resizing, rebuild/crop UV at the same texel density and re-pack without stretching or corrupting shared islands.
- Preserve cube and bone UUIDs, parent links, animation tracks and texture references. When restoring a decoration, restore its original parent bone and pivot; do not attach it to root merely to make it visible in edit mode. Verify all refs, remove stale refs for deleted elements.
- Large creatures: choose attack side with the gameplay camera and intended telegraph in mind. Prefer a clearly readable right-arm sweep for the right-handed root guardian; use a larger windup, torso movement and follow-through for heavy creatures, not a short arm jab. Do not force right-handed attacks on every creature. For animal anatomy, avoid flank cubes with no silhouette or functional purpose.

## Run the checks
Install requirements.txt. From the skill folder:

```bash
python scripts/check_z_fighting.py path/to/model.bbmodel --hz 20 --strict-near --output report.json
python scripts/check_uv.py path/to/model.bbmodel --output uv.json
python scripts/check_geometry.py path/to/model.bbmodel
python scripts/test_z_fighting.py
```

The face checker constructs cube corners, applies cube rotation and the hierarchical bone transforms (including numeric linear translation/rotation/scale tracks), constructs face normals, tests the plane distance, then clips the projected convex polygons to determine overlap area. AABB is only a broad-phase filter. `--hz 20` tests at least 20 samples/sec plus keyframe times and the rest pose. `--strict-near` fails for both exact and near same-facing candidates. Opposing normals are reported separately as possible contact: review exposed edges, opacity, culling and runtime before accepting. The script does NOT prove occlusion or decide which cube should be altered. A count of zero means no candidates in the sampled numerical approximation, not guaranteed absence of flicker. Nonlinear/Molang, inflate/rescale and noncube elements are unsupported; a flagged model must not be declared clean. The Euler/scale convention is an approximation; compare against the actual Blockbench/ModelEngine version. Continuous-time intersections, depth-buffer precision at different camera distances, alpha cutouts, animation blends, and shader effects require separate checks.

## Release checklist
1. Run geometry and UV validation and the rest-pose face check before texture painting.
2. Fix exact and near same-facing overlap, inspect opposite-facing contact separately, and rerun the checks after each fix. Do not add uniform offsets or blanket inflate/deflate.
3. Run all animation clips at >=20 Hz plus exact keyframes, including death squash, and check ground contact and attachment hierarchy. Explicitly report sampled issues, unsupported tracks and any exceptions. Never claim continuous or runtime safety from the script.
4. Render front, side, back, 3/4, and real-time movement. A deterministic software z-buffer may hide flicker; check in Blockbench and at multiple game viewing distances with actual ModelEngine resource pack. If runtime is unavailable, disclose it.
