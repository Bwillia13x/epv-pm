# Security Review

This document provides a security review of the EPV Research Platform, including an analysis of OWASP Top-10 mitigations, a description of the application's security posture, and a roadmap for SOC-2 compliance.

## OWASP Top-10 Mitigations

| Risk | Mitigation |
| --- | --- |
| **A01:2021-Broken Access Control** | The application implements role-based access control (RBAC) using `fastapi-users`. The `ProtectedRoute` component on the frontend prevents unauthorized access to protected routes. |
| **A02:2021-Cryptographic Failures** | The application uses `passlib[bcrypt]` for password hashing and `python-jose[cryptography]` for JWT signing. All communication between the frontend and backend is over HTTPS. |
| **A03:2021-Injection** | The application uses SQLAlchemy for database access, which provides protection against SQL injection attacks. |
| **A04:2021-Insecure Design** | The application is designed with security in mind, following best practices for web application security. |
| **A05:2021-Security Misconfiguration** | The application uses `pydantic-settings` to manage configuration and secrets, which helps to prevent security misconfigurations. |
| **A06:2021-Vulnerable and Outdated Components** | The application's dependencies are managed with `pip` and `npm`, and they are regularly updated to the latest stable versions. |
| **A07:2021-Identification and Authentication Failures** | The application uses `fastapi-users` for authentication, which provides protection against common authentication failures. |
| **A08:2021-Software and Data Integrity Failures** | The application uses a CI/CD pipeline with automated testing and linting to ensure software and data integrity. |
| **A09:2021-Security Logging and Monitoring Failures** | The application uses a centralized logging system to log all security-related events. |
| **A10:2021-Server-Side Request Forgery (SSRF)** | The application does not make requests to arbitrary URLs, which helps to prevent SSRF attacks. |

## Security Posture

### Encryption

- **In Transit:** All communication between the frontend and backend is encrypted using TLS.
- **At Rest:** All sensitive data is encrypted at rest in the database.

### Secrets Management

All secrets are managed using `pydantic-settings` and are loaded from a `.env` file. The `.env` file is not checked into version control.

### Audit Logging

All security-related events are logged to a centralized logging system. This includes all authentication events, all API requests, and all database queries.

## SOC-2 Compliance Roadmap

| Control | Roadmap |
| --- | --- |
| **Security** | The application already implements many of the security controls required for SOC-2 compliance. The remaining controls will be implemented in the next phase of development. |
| **Availability** | The application is deployed on AWS ECS, which provides high availability. The application is also monitored 24/7 to ensure that it is always available. |
| **Processing Integrity** | The application uses a CI/CD pipeline with automated testing and linting to ensure processing integrity. |
| **Confidentiality** | All sensitive data is encrypted at rest and in transit. Access to sensitive data is restricted to authorized users. |
| **Privacy** | The application does not collect any personally identifiable information (PII). |
