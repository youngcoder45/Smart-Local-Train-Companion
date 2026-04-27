# Security Policy

This document describes how to report security vulnerabilities for this repository and what you can expect from maintainers.

## Supported Versions

Security fixes are provided for the latest version of the codebase on the default branch.

If this project publishes tagged releases, only the **latest release** and the **default branch** are considered supported for security updates unless stated otherwise in release notes.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public GitHub Issue, Pull Request, or Discussion.

Instead, use one of the following private reporting channels (in order of preference):

1. **GitHub Security Advisories (Preferred)**
   - Go to: `Security` → `Advisories` → `Report a vulnerability`
   - Or open directly: `https://github.com/<OWNER>/<REPO>/security/advisories/new`

2. **Private contact (if GitHub Advisories is unavailable)**
   - If the repository provides a private security contact, use that channel.
   - Otherwise, reach out to the repository owner/maintainers through a private method you trust.

### What to Include

To help us verify and fix the issue quickly, include:

- A clear description of the vulnerability and its impact
- Affected components (frontend/backend/API/etc.)
- Steps to reproduce or a proof-of-concept (PoC)
- Any relevant logs, screenshots, or traces (remove secrets)
- Suggested fix or mitigation, if you have one
- Your assessment of severity (optional)

### Sensitive Data

Do not include:

- Credentials, access tokens, API keys, private keys
- Customer/user data
- Internal URLs or infrastructure details that should not be public

If sensitive data is required to reproduce, redact it or provide a safe mock.

## Coordinated Disclosure

We follow a coordinated disclosure process:

- We will acknowledge receipt of your report as soon as feasible.
- We will work to verify the vulnerability and determine severity.
- We will identify a fix, mitigation, and release strategy.
- Once a fix is available, we may publish a security advisory and/or release notes.

Please allow maintainers time to investigate before disclosing publicly.

## Reporting Non-Security Issues

If your report is not a security issue (for example: general bug, feature request, docs), please use the standard GitHub issue templates in this repository.

## Security Best Practices for Contributors

When contributing, please:

- Avoid committing secrets. Use environment variables and `.env` files that are excluded from version control.
- Validate and sanitize all untrusted input.
- Prefer secure defaults for authentication/authorization.
- Add tests for security-relevant behavior when possible.
- Keep dependencies up to date and avoid introducing vulnerable packages.

## Dependency Vulnerabilities

If you find a vulnerable dependency, include:

- Dependency name and version
- Advisory/CVE link (if available)
- Where it is used in the codebase
- Recommended patched version

## License

This security policy applies only to this repository and is subject to change.
