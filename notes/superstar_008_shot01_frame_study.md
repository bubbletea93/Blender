# Superstar #008 — Shot 01 reference analysis

Shot 01 is the establishing shot from BlendJam’s *Hippo Hide* reel. It lasts 33 frames at 24 fps, or 1.375 seconds. Blender frames 1–33 correspond to reference frames 0–32.

## Framing and action

The low grass-height camera looks slightly upward across a dark green, daisy-covered rise. The near flowers are soft and the middle distance is clearer. A pale blue, lightly clouded sky fills roughly the upper three-quarters of the frame. The pink-lavender flamingo is the stable visual anchor. Its arched neck faces left above a rounded, textured body. One leg is planted and the other bends back with its foot lifted. The flamingo occupies roughly four times the on-screen height of the tee.

The ghost tee is present from the first frame. It floats just above the field beside the flamingo with a mostly front-facing torso, alternating sleeve angles, and small rises and dips. In the Superstar interpretation, use the maroon Shaka Wear tee and its outlined star. Keep the bird’s framing similar in both versions and open up the lateral field of view for landscape.

- **Reference f0–f8**. The tee travels right while the bird stays near center. The tee starts to settle into its first visible dip.
- **Reference f9–f16**. The tee continues right and reaches its first low pose around f13–f15. Use subtle opposite sleeve swing and weight transfer.
- **Reference f17–f21**. The tee rises and its screen-right travel peaks around f20. Keep the torso readable while the camera begins reversing.
- **Reference f22–f28**. The tee moves back toward center and dips again. The foreground parallax becomes stronger.
- **Reference f29–f32**. The tee and nearer flowers sweep left with growing lateral blur. The flamingo remains near center. Use an accelerating move into the next cut.

## Frame observations

Pixel coordinates use a top-left origin on the 720 × 1280 source. Shirt X is the median of the segmented cream area. Top and bottom Y are the 3rd and 97th percentiles, so motion blur and dark folds can shift the readings by a few pixels. The last two columns are the median X and upper Y of the segmented flamingo silhouette above the feet.

| Reference frame | Time (s) | Tee X | Tee top Y | Tee bottom Y | Bird X | Bird upper Y |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.000 | 391 | 737 | 944 | 325 | 119 |
| 1 | 0.042 | 399 | 737 | 943 | 328 | 119 |
| 2 | 0.083 | 408 | 737 | 943 | 328 | 119 |
| 3 | 0.125 | 416 | 737 | 943 | 328 | 118 |
| 4 | 0.167 | 425 | 737 | 944 | 327 | 117 |
| 5 | 0.208 | 433 | 736 | 943 | 329 | 117 |
| 6 | 0.250 | 444 | 737 | 941 | 329 | 116 |
| 7 | 0.292 | 453 | 739 | 942 | 329 | 115 |
| 8 | 0.333 | 463 | 742 | 946 | 327 | 114 |
| 9 | 0.375 | 471 | 746 | 952 | 328 | 114 |
| 10 | 0.417 | 480 | 750 | 958 | 328 | 113 |
| 11 | 0.458 | 488 | 755 | 963 | 328 | 112 |
| 12 | 0.500 | 495 | 758 | 968 | 326 | 111 |
| 13 | 0.542 | 501 | 761 | 972 | 328 | 111 |
| 14 | 0.583 | 508 | 761 | 974 | 328 | 111 |
| 15 | 0.625 | 514 | 760 | 971 | 328 | 110 |
| 16 | 0.667 | 519 | 756 | 968 | 327 | 110 |
| 17 | 0.708 | 524 | 750 | 960 | 327 | 109 |
| 18 | 0.750 | 528 | 743 | 950 | 327 | 109 |
| 19 | 0.792 | 530 | 739 | 941 | 327 | 109 |
| 20 | 0.833 | 531 | 736 | 936 | 327 | 109 |
| 21 | 0.875 | 530 | 736 | 935 | 327 | 109 |
| 22 | 0.917 | 526 | 738 | 937 | 328 | 110 |
| 23 | 0.958 | 519 | 743 | 943 | 328 | 110 |
| 24 | 1.000 | 511 | 746 | 951 | 328 | 110 |
| 25 | 1.042 | 499 | 751 | 959 | 330 | 112 |
| 26 | 1.083 | 483 | 757 | 967 | 329 | 113 |
| 27 | 1.125 | 462 | 762 | 974 | 330 | 114 |
| 28 | 1.167 | 435 | 766 | 978 | 329 | 116 |
| 29 | 1.208 | 403 | 766 | 979 | 330 | 118 |
| 30 | 1.250 | 359 | 765 | 976 | 330 | 122 |
| 31 | 1.292 | 301 | 763 | 971 | 331 | 127 |
| 32 | 1.333 | 227 | 763 | 969 | 330 | 132 |

## Blender scene setup

The checked-in Shot 01 scenes are the first BlendJam motion study. The proposed Superstar set uses an oversized 8-ball and torn ruled notebook paper, with the low camera, cloudy sky, and walk timing from this study.

The Shaka Wear tee also has a [standalone editable asset](../assets/products/superstar_008_shaka_wear_cropped_tee.blend).

- [Portrait scene](../scenes/superstar_008_shot01_portrait_0_32.blend), 2160 × 3840.
- [Landscape scene](../scenes/superstar_008_shot01_landscape_0_32.blend), 3840 × 2160.
- Both scenes use frames 1–33 at 24 fps with the same low camera move, reframed for each aspect. The camera keys carry the late sweep and motion blur. The timeline marks the major reference beats.
- The Shaka Wear tee keeps its maroon colorway, white topstitching and distressed star. An embedded 66-bone KinemIQ walk supplies the sampled upper-body motion. The retargeted garment rig adds a small delayed hem response. The walk rig is hidden from rendering. [KinemIQ / Quaternius walk, CC0](https://github.com/Kinemiq/free-game-animations)
- The meadow and floral flamingo are authored 3D geometry. The sky uses a packed, CC0 environment by Greg Zaal. [Poly Haven Cloud Layers](https://polyhaven.com/a/cloud_layers)

[Original BlendJam reel](https://www.instagram.com/reels/C1kI2MRix40/) · [Local shot and frame index](../references/superstar_008/blendjam_hippo_hide/README.md)

## Review clips

[Portrait review](../renders/superstar_008_shot01_review/superstar_008_shot01_portrait_review.mp4) · [Landscape review](../renders/superstar_008_shot01_review/superstar_008_shot01_landscape_review.mp4)
