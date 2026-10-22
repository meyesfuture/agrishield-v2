# Punjab GrainWatch — Design System Specification

**Standard:** Google Material Clarity + Apple Typographic Restraint  
**Theme:** Light Agricultural Intelligence Theme  
**Primary Surfaces:** Warm white / clean neutral  
**Primary Accent:** Restrained agricultural green (`#166534`, `#15803d`, `#2e7d32`)

---

## 1. Color Palette & Surfaces

| Token | Value | Purpose |
| :--- | :--- | :--- |
| `--bg-canvas` | `#f8fafc` | Global background canvas (warm clean off-white) |
| `--bg-surface` | `#ffffff` | Primary container surface (cards, panels, header) |
| `--bg-surface-elevated` | `#f1f5f9` | Slightly recessed or secondary surface |
| `--bg-surface-hover` | `#e2e8f0` | Hover state background |
| `--text-primary` | `#0f172a` | High-contrast body and heading text (WCAG AAA) |
| `--text-secondary` | `#475569` | Secondary metadata and labels |
| `--text-muted` | `#64748b` | Tertiary caveats and footnotes |
| `--color-green-700` | `#15803d` | Primary agricultural brand green |
| `--color-green-800` | `#166534` | Deep green for buttons and active states |
| `--color-green-50` | `#f0fdf4` | Soft green tint for badges and positive highlights |
| `--color-amber-600` | `#d97706` | Warning / Insufficient data indicator |
| `--color-amber-50` | `#fffbeb` | Warning background tint |
| `--color-red-600` | `#dc2626` | Error / Blocked indicator |
| `--color-red-50` | `#fef2f2` | Error background tint |
| `--border-subtle` | `#e2e8f0` | Default card and divider borders |
| `--border-medium` | `#cbd5e1` | Input, select, and interactive borders |

---

## 2. Typography Scale

- **Font Family:** System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif`).
- **Headings:**
  - `h1`: `1.75rem` (28px), weight 700, line-height 1.25.
  - `h2`: `1.25rem` (20px), weight 600, line-height 1.35.
  - `h3`: `1.0rem` (16px), weight 600, line-height 1.4.
- **Body:** `0.875rem` (14px), weight 400, line-height 1.5.
- **Small / Meta:** `0.75rem` (12px), weight 500, line-height 1.4.
- **Monospace:** `"SF Mono", "Segoe UI Mono", "Roboto Mono", Menlo, Courier, monospace` for IDs, codes, quantities, and dates.

---

## 3. Elevation & Corner Radii

- **Card Radius:** `10px` (`--radius-card`)
- **Button Radius:** `6px` (`--radius-btn`)
- **Badge Radius:** `9999px` (Pill shape)
- **Shadows:**
  - Soft elevation: `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)`
  - Elevated panel: `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05)`

---

## 4. Accessibility & Interaction Invariants

1. **High Contrast Focus Visible:** All interactive elements must show a distinct `2px solid #166534` outline with `2px` offset when focused via keyboard (`:focus-visible`).
2. **Motion Reduction:** All animations and WebGL motion must honor `@media (prefers-reduced-motion: reduce)`.
3. **Screen Reader Landmarks:** Proper `role="main"`, `role="navigation"`, `role="banner"`, `aria-label`, and `scope="col"` on table headers.
4. **No Flashing / Distracting Animations:** Motion is purposeful and restrained.
