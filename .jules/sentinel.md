# Sentinel's Journal - Critical Learnings Only

## 2025-01-24 - Rate Limiting and Payload Protection
**Vulnerability:** Missing rate limiting and payload size limits on public POST endpoints (like /api/contact) can lead to spam and DoS.
**Learning:** Flask's `MAX_CONTENT_LENGTH` is a global setting that provides a first line of defense against large payload attacks. A simple in-memory sliding window rate limiter using `request.remote_addr` is effective for small-scale applications where adding a full-blown dependency like `Flask-Limiter` might be overkill.
**Prevention:** Always set `MAX_CONTENT_LENGTH` in Flask apps and implement at least basic rate limiting on all public write endpoints.
