# Sentinel's Journal - Critical Learnings Only

## 2025-01-24 - Information Leakage via JSON Error Responses
**Vulnerability:** API endpoints were returning raw exception details using `str(e)` in JSON responses, leaking internal paths and subprocess errors.
**Learning:** In Flask apps, catching all exceptions and returning `str(e)` in the response body is a common but insecure pattern that exposes internal application state.
**Prevention:** Use a generic error message for the client and log the detailed exception to `app.logger.error` for developer investigation.

## 2025-01-24 - State-Changing Actions via GET Requests
**Vulnerability:** The `/api/wallpapers/repack` endpoint, which triggers a heavy subprocess, was accessible via GET requests.
**Learning:** Using GET for operations that modify server state (like repacking assets) is a CSRF risk and can lead to accidental execution.
**Prevention:** Always use POST (or other non-safe methods) for state-changing operations and explicitly define them in the `@app.route(..., methods=['POST'])` decorator.
