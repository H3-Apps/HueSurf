# Sentinel's Journal - Critical Learnings Only

## 2026-02-01 - [State-changing GET endpoints]
**Vulnerability:** The `/api/wallpapers/repack` endpoint was using the `GET` method to trigger a resource-intensive repacking process on the server.
**Learning:** Developers sometimes use `GET` for simple API triggers, forgetting that these can be easily exploited via CSRF or accidental navigation.
**Prevention:** Always use `POST`, `PUT`, or `DELETE` for any endpoint that modifies server state or triggers significant background processes. Enforce this in routing decorators.
