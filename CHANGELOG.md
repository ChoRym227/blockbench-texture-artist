# Changelog

## v3.1
- Improved focal weapon texture readability rules for staffs and lanterns.
- Added rear-silhouette cleanup guidance to prevent awkward boxy support cubes behind weapons.
- Updated Frost Witch example with cleaner lantern texture and removed rear support cube.

# v3 — Weapon design and pose

- Retain V2 humanoid, fabric, anti-line-cube and per-face UV rules.
- Add weapon detail hierarchy, motif design, independent directional UV, copy-on-write for shared faces.
- Add separate wrist/weapon grip hierarchy and weapon-class pose guidance.
- Add numeric 20 Hz grip/axis/ground/OBB review and per-face UV validation.
- Frost Witch V3 example: engraved staff, separate hand, corrected forearm and keyed wrist.
- Runtime compatibility remains untested.

# v2 — Geometry quality update

- Added mandatory silhouette/blockout review before UV creation.
- Added humanoid anatomy and joint placement guidance.
- Added cloak/robe construction, cutout and animation rules.
- Added anti-line-cube checks and geometry review helper.
- Preserved dimension-matched per-face UV and intentional UV reuse rules.
- Clarified that image generation must not substitute for skill updates or editable models.
