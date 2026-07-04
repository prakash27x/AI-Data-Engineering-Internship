# NEPSE Financial Report Analyzer Project Plan

## 1. Project Purpose

NEPSE Financial Report Analyzer is a public, retail-investor-friendly platform for reviewing company financial reports, comparing listed companies, and exploring financial trends without any login requirement.

The product is designed as a static, multi-page frontend prototype at this stage. Its purpose is to present the intended user experience, navigation flow, and visual system before the full backend data pipeline is implemented.

## 2. Core Product Goals

- Provide open access to NEPSE financial report insights for retail investors, researchers, and students.
- Make report exploration simple with clear navigation between upload, dashboard, and comparison views.
- Keep the interface responsive across mobile, tablet, and desktop.
- Support theme switching for comfort in different viewing conditions.
- Reduce friction with keyboard shortcuts and lightweight help cues.
- Use a clear extraction workflow based on PDF tools such as PyMuPDF, not AI-based extraction.

## 3. Audience

The primary audience is retail investors who want quick access to public financial data.

Secondary audiences include:

- Students studying financial statements or stock market analysis.
- Researchers reviewing company performance over time.
- Analysts comparing NEPSE-listed companies across sectors.

## 4. Design Direction

The design resources provided for the project define a corporate, high-trust visual language. The interface should feel like a financial terminal rather than a marketing website.

### Visual Principles

- Deep navy and corporate blue establish trust and seriousness.
- Light greys and tonal surfaces keep data readable and reduce distraction.
- Strong hierarchy helps users scan numbers, charts, and comparison tables quickly.
- Cards and panels should feel structured, compact, and consistent.
- Motion should be subtle and purposeful, not decorative.

### Typography

- Inter is the primary font family.
- Headlines should be bold and high-contrast.
- Data-heavy sections should favor legibility over ornament.
- Labels and helper text should remain smaller and quieter than primary metrics.

## 5. Information Architecture

The project is organized into a simple public flow:

1. Landing page introduces the product and explains the value proposition.
2. Upload page accepts public report inputs and shows the extraction workflow.
3. Dashboard page presents company-level metrics, charts, and analysis summaries.
4. Comparison page shows side-by-side company analysis.

The architecture intentionally avoids duplicate navigation. Sidebar navigation is the primary site-wide navigation pattern on the internal pages, while the landing page remains standalone.

## 6. Page Responsibilities

### Landing Page

The landing page is the public entry point. It should:

- Explain the product in clear, accessible language.
- Emphasize that reports are publicly accessible.
- Show key benefits, supported sectors, and the basic workflow.
- Direct users into the upload or dashboard flow.

### Upload Page

The upload page is the report intake surface. It should:

- Make the public-access model obvious.
- Present file upload, report metadata, and duplicate detection cues.
- Explain that the extraction step uses a PDF toolchain such as PyMuPDF.
- Keep upload controls large and visible on mobile devices.

### Dashboard Page

The dashboard page is the main analysis workspace. It should:

- Show financial summary cards and trend charts.
- Present summary insights in a clear, readable layout.
- Support quick navigation between related views.

### Comparison Page

The comparison page is for side-by-side evaluation. It should:

- Compare metrics between two companies.
- Highlight deltas, growth direction, and risk signals.
- Remain readable on smaller screens by stacking content vertically.

## 7. Interaction Plan

The project uses lightweight interactions to keep the static prototype usable:

- Theme toggle persists in localStorage.
- Mobile hamburger navigation toggles the sidebar.
- Keyboard shortcuts support fast movement between main pages.
- Help text provides shortcut discovery.
- Upload area feedback responds to drag and drop events.

### Keyboard Shortcuts

- U: Upload page
- D: Dashboard page
- C: Comparison page
- T: Toggle theme
- ?: Show keyboard shortcuts help

## 8. Responsive Strategy

The layout follows a mobile-first approach.

- On mobile, controls should remain visible, touch targets should be larger, and navigation should collapse into a hamburger menu.
- On tablet, content should stack cleanly and preserve scanability.
- On desktop, the sidebar, charts, and cards should expand into a fuller layout.

The goal is not to simply shrink the desktop interface, but to preserve the task flow on smaller screens.

## 9. Data Extraction Plan

The extraction process is not AI-based.

The intended approach is to use PDF processing tools such as PyMuPDF to read report content, extract structured tables and text, and then normalize the values for display and comparison.

This matters because the product should be positioned as a document-processing and analysis tool, not as a generative AI system.

## 10. Accessibility and Usability

The documentation and UI planning should prioritize:

- Clear labels on all major controls.
- Adequate touch target size on mobile.
- High color contrast for primary actions and important status indicators.
- Keyboard discoverability through visible shortcuts help.
- Avoiding redundant navigation that increases cognitive load.

## 11. Current Implementation Status

### Completed

- Landing page created and styled.
- Public-access positioning clarified.
- Theme switching added.
- Keyboard shortcut help added.
- Mobile sidebar toggle introduced.
- Duplicate top navigation removed from internal pages.
- Upload and comparison views aligned with the shared design system.

### In Progress or Next

- Continue refining mobile visibility and spacing.
- Replace any remaining AI-based wording with PDF-processing language where needed.
- Build the actual backend extraction workflow with a library such as PyMuPDF.
- Connect extracted data to a persistent storage layer.

## 12. Recommended Next Phases

### Phase 1: Frontend Polish

- Finalize responsive behavior across breakpoints.
- Check visibility of all mobile controls.
- Ensure the landing page reflects the final positioning accurately.

### Phase 2: Extraction Pipeline

- Implement PDF parsing and field extraction.
- Validate extracted report data against sample NEPSE filings.
- Add duplicate detection and normalization rules.

### Phase 3: Data Storage and Serving

- Store extracted data in a database.
- Serve dashboard and comparison views from persisted records.
- Add report history and filtering.

### Phase 4: Product Hardening

- Add validation, error handling, and quality checks.
- Document supported report formats.
- Refine labels, help text, and onboarding flow.

## 13. Summary

The project is planned as a public, responsive NEPSE analysis interface with a strong corporate visual identity and a document-processing extraction pipeline. The main design intent is clarity, trust, and fast access to report data, while the main technical intent is to use reliable PDF tooling such as PyMuPDF for extraction instead of AI-based parsing.
