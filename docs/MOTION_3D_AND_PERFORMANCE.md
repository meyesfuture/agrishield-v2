# 3D, Motion & Performance Brief

## Landing-page hero concept

Create an original, lightweight 3D scene inspired by Punjab's grain landscape: stylized crop rows or topographic field contours, a clean modern silo/grain-storage form, sunlit haze and a few floating data glints. Keep the scene symbolic; do not imply it depicts a real facility or actual stock quantity. Art direction: tactile, precise, minimal and premium.

## Implementation requirements

- Build a single self-contained scene using Three.js/React Three Fiber only if the environment supports it.
- Prefer procedural geometry/materials over large paid assets. Include asset license/source information for any external model.
- Do not download an unlicensed warehouse model or use real private facility coordinates.
- Lazy-load 3D after the initial headline/navigation; ensure it cannot block the dashboard.
- Respect reduced motion: no automatic rotation/parallax when `prefers-reduced-motion` is enabled.
- Pause or reduce animation when the tab is hidden or the hero leaves the viewport.
- Cap device pixel ratio, polygons, shadows and draw calls to reduce GPU usage.
- Provide a static CSS/SVG/optimized-image fallback when WebGL is unavailable or the scene fails.
- Maintain text contrast over the scene; prevent scene from intercepting clicks to page controls.
- Use subtle transitions across buttons/cards/filter states/charts; do not impose infinite movement on every component.

## Acceptance checks

- The landing page remains usable if the 3D bundle fails.
- The hero does not cause a measurable blocking delay for title/nav content.
- Keyboard focus and screen-reader order remain correct.
- Reduced-motion mode is visibly quieter.
- Test on an integrated-GPU/lower-end device profile and a mobile viewport.
- Do not claim real-world warehouse detection based on the visual scene or single raster sample.
