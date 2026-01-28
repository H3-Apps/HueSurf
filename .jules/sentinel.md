# Sentinel's Journal - Critical Learnings Only


## 2024-05-20 - Enforce POST-Only Access for State-Changing Endpoints
**Vulnerability:** A development-only endpoint (`/api/wallpapers/repack`) that triggers a significant server-side action (repacking all wallpapers) was accessible via a `GET` request.
**Learning:** Allowing a state-changing operation to be triggered by a `GET` request introduces a Cross-Site Request Forgery (CSRF) vulnerability. An attacker could trick a logged-in developer into visiting a malicious page that contains an image tag (`<img src=".../api/wallpapers/repack">`), causing their browser to trigger the action unintentionally.
**Prevention:** All endpoints that cause a change in the server's state (e.g., creating, updating, deleting resources) MUST be protected by restricting them to `POST`, `PUT`, `PATCH`, or `DELETE` methods. This ensures that the action cannot be triggered by simple, cross-site URL access.
