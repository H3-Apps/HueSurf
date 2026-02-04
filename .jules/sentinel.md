# Sentinel's Journal - Critical Learnings Only

## 2025-01-24 - Comprehensive Security Hardening of Flask App
**Vulnerability:** Multiple security gaps including missing security headers, information leakage in API error responses, lack of input validation on contact form, and insecure GET method for state-changing operations.
**Learning:** Hardening a Flask application requires multiple layers: `@app.after_request` for global headers, sanitizing all `Exception` and `subprocess` outputs to the client, and strictly enforcing HTTP methods (POST for state changes).
**Prevention:** Always use a security header middleware, implement a generic error response wrapper that logs details internally but keeps client messages vague, and validate all incoming JSON payload lengths and types.
