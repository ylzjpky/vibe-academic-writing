# Security Policy

## Supported versions

Security fixes are applied to the latest tagged release. Older versions may not receive backports.

## Reporting a vulnerability

Do not report vulnerabilities in a public issue when the report contains or could reveal credentials, session data, signed URLs, private institutional resources, or personal information.

Use GitHub's private vulnerability reporting feature for this repository. If that feature is unavailable, contact the maintainer through the private contact method listed on the maintainer's GitHub profile. Include the affected version, a minimal reproduction using synthetic data, impact, and suggested mitigation. Do not include real school credentials or course materials.

## Credential exposure

If credentials, cookies, authorization headers, recovery codes, or signed URLs are exposed:

1. Stop sharing or publishing the affected artifact.
2. Revoke or rotate the exposed credential through the relevant institution or provider.
3. Remove the data from the working tree and repository history where necessary.
4. Run the bundled sensitive-artifact scanner and repository tests.
5. Notify affected parties through an appropriate private channel.

Deleting a file in a later commit does not remove it from Git history.

## Security boundaries

This project does not authorize bypassing access controls, paywalls, CAPTCHA, robots controls, download restrictions, rate limits, or institutional policy. Users must perform credential and MFA entry directly in the provider's interface. The skill must not persist secrets or delegate authenticated browser control to multiple agents.

Security reports about misuse that requires violating these boundaries may be closed without action.
