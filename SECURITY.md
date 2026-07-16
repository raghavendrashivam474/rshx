# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.8.x   | Yes       |
| < 0.8   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in RSHX, please report it
by emailing raghavendrashivam474@gmail.com rather than opening a
public issue.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix if available

You will receive a response within 48 hours.

## Security Considerations

RSHX executes commands on the user's system with the permissions
of the running user. Users should:

- Only run .rshx scripts from trusted sources
- Only install plugins from trusted sources
- Review script contents before execution
- Be aware that scripts share the active shell environment
