## 2026-02-06 - [Accessible Toggle Pattern]
**Learning:** Custom interactive toggles built with `<div>` or `<span>` are not accessible to keyboard users or screen readers. Using a `<button type="button" role="switch">` with `aria-checked` ensures the element is focusable, has a clear interactive role, and communicates its state correctly.
**Action:** Always use semantic buttons with appropriate ARIA roles and states for custom toggle switches.
