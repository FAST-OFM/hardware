# Prescan Camera Mounting Notes

## Goal

Provide a repeatable overview image of the slide for tissue-map generation.

## Requirements

- Rigid mount relative to the stage coordinate system.
- Stable illumination.
- Field of view large enough for whole slide or tiled overview.
- Calibration target accessible for prescan-to-stage transform.
- No interference with high-resolution objective path.

## Calibration implications

Any movement of the prescan camera, lens or illumination invalidates:

- prescan flat-field;
- prescan lens distortion;
- prescan-to-stage transform;
- tissue segmentation parameters if illumination changes strongly.
