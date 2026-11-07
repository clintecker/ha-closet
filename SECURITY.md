# Security

Report vulnerabilities through this repository's private vulnerability reporting.
Do not publish tokens, catalogs, photographs, household configuration or raw
diagnostics in a public report.

The API authenticates clients. HA-backed catalog sync and generation require an
authenticated administrator. The dedicated adapter credential is not an owner
token and only trusted adapter requests may carry HA actor assertions.
Ingress accepts only the configured Supervisor peer and requires the browser
request marker for writes. Do not expose the ingress listener as a public API.

Catalogs and credentials belong in private runtime storage. The public examples,
screenshots and container must not contain real inventory or deployment state.
Product reference images and the optional configured AI provider are external
services; neither is required for offline validation.
