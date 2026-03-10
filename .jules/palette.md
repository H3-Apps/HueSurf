## 2025-01-24 - Accessible Toggles and Icon Buttons
**Learning:** Custom UI elements like toggle switches created with `div` tags are inaccessible to keyboard users and screen readers. Converting them to `<button type="button" role="switch">` with `aria-checked` and adding `:focus-visible` styles with sufficient contrast (e.g., `2px solid #dc2626`) significantly improves accessibility.
**Action:** Always use semantic button elements for interactive toggles and ensure all icon-only buttons have descriptive `aria-label` attributes.
