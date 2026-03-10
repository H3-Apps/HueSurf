## 2026-02-02 - Template Inheritance Fix for Broken Subpages
**Learning:** In projects where multiple subpages extend a base template, the base template must include `{% block content %}` and other necessary blocks. Without these, subpages appear to "render" the landing page content (the base content), which is a major UX fail.
**Action:** Always verify that `base.html` includes proper block placeholders and that subpages correctly override them.

## 2026-02-02 - Accessible Toggles with Semantic Buttons
**Learning:** Custom toggles implemented as `div` elements are not keyboard accessible or screen-reader friendly. Converting them to `<button type="button" role="switch">` with `aria-checked` and `:focus-visible` styles provides an immediate, standard-compliant accessibility win.
**Action:** Replace non-semantic interactive `div` elements with appropriate ARIA-enabled semantic elements like `<button>`.
