# EPV Research Platform – Investor-Grade Upgrade Package

## 1 – Snapshot of the Current Build

### Strengths
• Rich domain logic: EPV, DCF, portfolio optimisation, alt-data, PDF reports.
• Modular directory structure (`src/analysis`, `src/api`, `src/data`, …).
• Full-stack demo (FastAPI + React) with containerisation and CI (lint → unit-tests → builds).
• Initial security posture (OWASP table, RBAC skeleton).
• Extensive unit tests for risk utility and data gateway.

### Key Gaps & Risks
• Data layer is almost entirely mock / Yahoo Finance scraping; no persistent DB in production path.
• Asynchronous patterns mix blocking (e.g. `yfinance`) and async I/O → latent scalability issues.
• Test coverage sits ~30-40 % (coverage gate in CI is 80 %).
• No formal package version pins or SBOM; supply-chain risk unchecked.
• Demo secrets (`SECRET`) hard-coded; OAuth/JWT not integrated end-to-end.
• Front-end build served on port 80 without TLS; CORS set to "".
• Observability limited to console logs; no tracing, metrics, or alerting.
• Docker images not slimmed; build uses root user.
• SOC-2 roadmap is only documentation; no evidence of controls (back-ups, DR, logs, MFA).
• PDF generation depends on ReportLab and WeasyPrint yet not declared in Dockerfile; breakage risk.
• Performance: Monte-Carlo defaults to 10 k simulations synchronously—blocks event loop.
• Licensing & compliance checks absent (important for funding rounds).

---

## 2 – Phased Upgrade Plan to Investor-Grade

### Phase 0 – Governance & Road-Mapping (Week 0)
• Define Definition-of-Done for "investor-grade" (uptime > 99.9 %, PII handling, SLA, etc.).
• Freeze feature scope; create RFC template for future features.

### Phase 1 – Codebase Hygiene (Weeks 1-2)
1. Enforce 100 % typed public API surface (`mypy --strict`).
2. Adopt `pre-commit` with Black, isort, Ruff, safety, commitizen.
3. Elevate test coverage threshold to 90 %; write missing tests (focus on `analysis.*`).
4. Replace hard-coded secrets with `pydantic-settings` loaded from AWS Secrets Manager or HashiCorp Vault.

### Phase 2 – Reliable Data & Persistence (Weeks 2-4)
1. Introduce SQLAlchemy 2 async models; move all "mock" collections to Postgres.
2. Abstract data providers behind a strategy pattern; plug in paid APIs (Alpha Vantage, Tiingo, Intrinio).
3. Add Alembic migrations; run in CI.
4. Implement caching layer with Redis (supersede pickle files).

### Phase 3 – Scalable Backend (Weeks 4-6)
1. Replace blocking calls with `httpx.AsyncClient`; run with Uvicorn workers and Gunicorn.
2. Rate-limit per-user via Redis tokens.
3. Integrate OpenTelemetry tracing; ship to Grafana Cloud.
4. Add health/readiness/metrics endpoints (`/metrics` → Prometheus).

### Phase 4 – Production-Grade Front-End (Weeks 5-7, parallel)
1. Promote React demo to Vite + MUI v5; add Cypress e2e tests and Storybook.
2. Use OAuth2 Code flow (PKCE) with FastAPI Users; store tokens in HttpOnly cookies.
3. Bundle static site; serve via Nginx side-car behind TLS (LetsEncrypt in dev, ACM in prod).

### Phase 5 – DevOps & CI/CD (Weeks 6-8)
1. Switch CI to GitHub Actions matrix (3.10 – 3.12); add SAST (Semgrep) and dependency scanning (Dependabot/Snyk).
2. Tag images with git-sha; push to ECR/GHCR; sign with Cosign.
3. Terraform module for AWS ECS + RDS + ElastiCache + CloudFront.
4. Blue/Green deploy workflow; smoke tests post-deploy.

### Phase 6 – Security & Compliance (Weeks 8-10)
1. Threat-model & pentest; fix gaps (CSP headers, JWT rotation, input validation).
2. Enable AWS Shield for DDoS, GuardDuty for threat detection.
3. Implement audit logging (user, data access) with retention ≥ 1 year.
4. SOC-2: map controls to automated evidence (CI logs, CloudTrail, IAM).

### Phase 7 – Performance & Cost Optimisation (Weeks 9-11)
1. Profile hot paths (Monte-Carlo, EPV loops); vectorise with NumPy or run in worker pool (Celery/RQ).
2. Add autoscaling policies on CPU / queue length.
3. Cache immutable PDF reports on S3 + CloudFront.

### Phase 8 – Documentation & Investor Collateral (Weeks 10-12)
• Autogenerate API docs (Redoc, Swagger) with examples.
• Sphinx + MkDocs for dev docs; coverage badges, architecture diagrams.
• Produce KPI dashboard (ARR potential, user adoption) fed from Postgres.
• Draft investor pitch deck highlighting moat (EPV IP, proprietary alt-data scoring).

---

## 3 – Agentic Prompts (Tasks 1-6)

### 1 – ⚙️ Agent-Static-Audit
Clone repository at given commit. Run Surfraw/Ruff, MyPy `--strict`, safety, and Semgrep. Produce a markdown report: **category, file, line, rule, remediation suggestion**. Prioritise critical & major issues.

### 2 – 🧪 Agent-Coverage-Boost
Target modules under `src/analysis/` with < 70 % coverage. Auto-generate parametrised PyTest suites until project coverage ≥ 90 %. Ensure deterministic tests and total runtime < 60 s.

### 3 – 🔐 Agent-Secret-Scanner
Search entire repo (including history) for hard-coded secrets, keys or passwords. Replace with environment variable placeholders (`${VAR}`). Update docs. Deliver one PR per secret group.

### 4 – 🛢 Agent-DB-Migration
Design Postgres schema for entities: `company_profile`, `financial_statement`, `market_data`, `user`, `report`. Generate Alembic migrations and SQLAlchemy async models with indexes on `symbol`. Maintain referential integrity.

### 5 – 🚦 Agent-Async-Refactor
Refactor blocking IO in `src/data/` & `src/analysis/` to asyncio with `httpx.AsyncClient`. Benchmark `GET /api/v1/analysis/AAPL` (with 5 peers) before/after; aim for 4× throughput improvement.

### 6 – 🐳 Agent-Docker-Harden
Produce multi-stage Dockerfile: builder (Poetry) → final Alpine image running as non-root. Keep image < 300 MB. Add Trivy scan step in CI; fail on high/critical vulnerabilities.

> **Note:** Agents 7-12 are defined in `AGENTS_EXT.md` for later phases.