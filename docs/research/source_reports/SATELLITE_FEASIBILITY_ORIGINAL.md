# Satellite feasibility

## Current result: conditional feasibility; no imagery acquired

The only successful satellite test was a public Copernicus Data Space catalogue metadata request. It returned a generic Sentinel-3 product record outside Punjab because the probe was not geographically or temporally filtered. This proves the metadata endpoint responded from this environment; it does not prove Punjab Sentinel-2 coverage, image download authorization, or warehouse detection performance. No raster pixels were acquired or analyzed.

## Best-fit imagery and use

- **Sentinel-2 optical, 10 m bands:** useful for crop phenology/area context and large exposed-yard change. Cloud, haze, harvest timing, and mixed pixels limit interpretation. It cannot see indoor grain stock.
- **Sentinel-1 SAR, 10 m class:** cloud-penetrating change observations can supplement optical time series and detect some surface/structure changes. Speckle, geometry, and changing moisture affect signals. It cannot identify wheat/paddy inside a roofed warehouse.
- **Commercial very-high-resolution imagery:** could assess building/yard expansion or truck/stockpile activity, subject to licensing, cost, and resolution-access rules. Not acquired; no purchase authorized.

## Reproducible next test

1. Define a fixed AOI from authorized Punjab district polygons; record CRS, boundary vintage, and checksum.
2. Query Sentinel-2 L2A and Sentinel-1 GRD scenes for pre-harvest, procurement peak, and post-season windows. Store query geometry, date window, product ID, cloud percentage, processing baseline, and retrieval timestamp.
3. First acquire a single public sample scene for a known Punjab location and a second date. Log whether discovery and pixel download both work; discovery alone is not data acquisition.
4. Validate imagery coverage and preprocessing: cloud mask for optical, orbit/polarization/incidence consistency for SAR, reprojection and pixel-size preservation.
5. Compare only observable proxies (crop condition/harvest timing, large-yard activity, structure change) against independent field observations. Do not label hidden stock or legal intent from pixels.

## Bar for operational use

Satellite data can help prioritize field checks if the AOI, dates, quality masks, repeatability, and ground validation are available. It is not a standalone hoarding detector. To evaluate utility, assemble independently verified warehouse locations and dated inspections with both positive and negative examples, then measure precision/recall at the field-check unit. No such ground-truth set is currently available.
