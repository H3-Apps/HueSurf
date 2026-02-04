## 2025-05-15 - Accessible Settings Toggles

**Learning:** Implementing interactive toggles as `div` tags makes them invisible to keyboard users and screen readers. Using semantic `<button role="switch">` with `aria-checked` provides a standard, accessible interaction pattern. Adding global `focus-visible` styles ensures keyboard navigation is usable without impacting the visual design for mouse users.

**Action:** Always use semantic `<button>` elements for toggles and ensure `focus-visible` outlines are present for all interactive elements.
