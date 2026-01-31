# Sentinel's Journal - Critical Learnings Only

## 2026-01-31 - [Information Leakage via detailed Error Messages]
**Vulnerability:** API endpoints were returning raw exception strings (`str(e)`) and subprocess `stderr` output in JSON responses.
**Learning:** Returning internal error details can expose the server's directory structure, installed packages, and other environmental information to an attacker.
**Prevention:** Always catch exceptions and return generic, user-friendly error messages in API responses, while logging the detailed error server-side for debugging.

## 2026-01-31 - [Insecure HTTP Method for State-Changing Operations]
**Vulnerability:** The `/api/wallpapers/repack` endpoint, which triggers a resource-intensive disk operation, was accessible via a `GET` request.
**Learning:** Using `GET` for operations that change server state (like generating files) violates REST principles and makes the endpoint vulnerable to Cross-Site Request Forgery (CSRF) via simple image tags or links.
**Prevention:** Use `POST` (or other appropriate methods like `PUT`/`DELETE`) for any operation that modifies server state, and ensure the backend enforces these methods.
