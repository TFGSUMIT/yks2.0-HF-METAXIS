# Security Policy

METAXIS is pre-release research software. Do not use it for production or
consequential actions.

## Report a vulnerability

Use GitHub private vulnerability reporting when enabled. Do not disclose
credentials, tokens, private model inputs, or exploitable details in a public
issue.

## Security boundaries

- Provider credentials must come from an external secret authority.
- Models may propose actions but never own authorization or privilege.
- Tool execution must validate declared authority and fail closed.
- Prompts, tool schemas, evaluation inputs, and operational state must remain
  exportable from any provider.
- Logs and evidence must exclude secrets and respect declared data boundaries.

