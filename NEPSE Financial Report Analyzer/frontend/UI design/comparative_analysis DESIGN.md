---
name: Financial Data Interface
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#45474d'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545e76'
  primary: '#051125'
  on-primary: '#ffffff'
  primary-container: '#1b263b'
  on-primary-container: '#828da7'
  inverse-primary: '#bbc6e2'
  secondary: '#47607e'
  on-secondary: '#ffffff'
  secondary-container: '#c2dcff'
  on-secondary-container: '#48617e'
  tertiary: '#191000'
  on-tertiary: '#ffffff'
  tertiary-container: '#342300'
  on-tertiary-container: '#b0872f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#bbc6e2'
  on-primary-fixed: '#101b30'
  on-primary-fixed-variant: '#3c475d'
  secondary-fixed: '#d1e4ff'
  secondary-fixed-dim: '#afc9ea'
  on-secondary-fixed: '#001d36'
  on-secondary-fixed-variant: '#2f4865'
  tertiary-fixed: '#ffdea4'
  tertiary-fixed-dim: '#efc062'
  on-tertiary-fixed: '#261900'
  on-tertiary-fixed-variant: '#5d4200'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 24px
  gutter: 16px
---

## Brand & Style
The design system is engineered for the high-precision environment of stock market analysis. It prioritizes **trust, clarity, and institutional stability**. The aesthetic follows a **Corporate Modern** style, characterized by a structured layout, high-density information architecture, and a restrained use of color to ensure that critical market movements are immediately visible. 

The target audience consists of professional and retail investors who require a sophisticated, distraction-free environment to process real-time financial data. The interface should feel like a premium terminal—authoritative and reliable—using a limited color palette and systematic spacing to reduce cognitive load during volatile market sessions.

## Colors
The palette is rooted in **Deep Navy** and **Corporate Blue** to establish a sense of traditional financial security. 

- **Functional Colors:** Emerald Green and Crimson are reserved strictly for market performance indicators (Bullish/Bearish trends). These should be used with sufficient contrast against the neutral background to ensure accessibility.
- **Accents:** Professional Gold is used sparingly for premium features, active selection highlights, or specific milestone achievements.
- **Backgrounds:** A tiered system of light greys distinguishes between the application canvas and individual data containers, maintaining a clean and breathable workspace.

## Typography
This design system utilizes **Inter** for its exceptional legibility in data-dense environments. 

- **Numeric Data:** For tables and tickers, use tabular figures (`tnum`) to ensure that columns of numbers align vertically, facilitating quick comparison of stock prices and volumes.
- **Hierarchy:** Use bold weights for primary ticker symbols and currency amounts.
- **Labels:** Small caps or increased letter spacing should be applied to secondary labels to differentiate them from actionable data.
- **Scaling:** On mobile devices, `display-lg` should scale down to `headline-md` to maintain layout integrity without excessive wrapping.

## Layout & Spacing
The layout employs a **fixed-fluid hybrid grid**. The main sidebar navigation is fixed at 260px, while the main content area utilizes a 12-column fluid grid.

- **Grid Logic:** Use a 16px gutter between data widgets.
- **Data Density:** In complex tables, use a "compact" vertical rhythm (8px padding) to maximize the information visible above the fold. 
- **Responsiveness:** 
  - **Desktop:** Sidebar visible, 12-column grid.
  - **Tablet:** Sidebar collapses to icons, 8-column grid.
  - **Mobile:** Bottom navigation bar, 4-column grid, 16px margins.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** rather than aggressive shadows to maintain a flat, professional look suitable for financial terminals.

- **Level 0 (Canvas):** The base background using the neutral light grey.
- **Level 1 (Widgets/Cards):** White surfaces with a very subtle 1px stroke (#E0E4E8) and a soft, low-opacity shadow (4px blur, 2% opacity) to define boundaries.
- **Level 2 (Dropdowns/Modals):** Increased elevation with a more pronounced shadow to indicate temporary overlay and focus.
- **Charts:** Use a "Plotly-style" approach where the chart area is slightly inset or outlined with a faint grid to separate it from the card's metadata.

## Shapes
The design system uses a **Soft** shape language. 

- **Primary Elements:** A 4px (0.25rem) radius is applied to buttons, input fields, and small badges to provide a modern feel without appearing overly casual.
- **Large Containers:** Data cards and dashboard panels use an 8px (0.5rem) radius.
- **Interactive States:** Hover states on list items or table rows should use a 4px radius on the background highlight to maintain the geometric discipline of the system.

## Components
Consistent implementation of components ensures the platform feels like a unified tool.

- **Data Cards:** Must include a header area for the metric title and a footer area for "Time since last update" or "Percentage change."
- **Buttons:** 
  - *Primary:* Deep Navy background with White text.
  - *Secondary:* Transparent background with Corporate Blue border.
  - *Action:* Small, icon-only buttons for "Add to Watchlist" or "Alerts."
- **Charts:** Use a clean line-weight (2pt) for sparklines. Area charts should use a gradient fill with 10% opacity of the line color.
- **Status Badges:** Use "Pill" shapes for statuses like "Market Open" (Success) or "Market Closed" (Secondary Blue).
- **Tabs:** Underlined style with the Professional Gold accent for the active state, ensuring the label remains legible in `label-md` bold.
- **Input Fields:** Clean, bordered boxes with 14px text. Focus states should use a 2px Corporate Blue glow.