# EPV Research Platform – Static Analysis Audit (Task 1)

_Audit date: 2025-06-26_

---

## Legend
| Severity | Meaning |
| -------- | ------- |
| 🔴 **Critical** | Must fix before prod / investor demo |
| 🟠 **Major**    | Should fix during hardening phase |
| 🟡 **Minor**    | Nice-to-have / hygiene |

Each finding: **Category • File :Line • Rule • Summary → Suggested Fix**

---

## 1. Ruff `v0.x`  (lint)

| Sev | File:Line | Rule | Summary | Suggested Fix |
|-----|-----------|------|---------|---------------|
| 🟠 | `src/main.py:311` | `F541` | f-string with no placeholders | Remove `f` prefix or add placeholder |
| 🟠 | `src/main.py:318` | `F541` | f-string with no placeholders | Same as above |
| 🟠 | `src/main.py:329` | `F541` | f-string with no placeholders | Same |
| 🟡 | `src/utils/cache_manager.py:7` | `F401` | Unused import `time` | Delete unused import |
| 🟡 | `src/utils/rate_limiter.py:7` | `F401` | Unused import `List` | Delete or use generic alias |
| 🟡 | `src/ui/web_app.py` (multiple) | `F401` | Many unused imports (`plotly.graph_objs`, `numpy`, `datetime`, `logging`) | Trim imports |
| 🟠 | `start_demo.py:73` | `E722` | Bare `except` | Catch specific exception types |
| 🟠 | `start_demo.py:80` | `E722` | Bare `except` | Same |
| _(≈70 additional minor `F401/F841` unused-code warnings omitted)_ |

**Ruff summary:** 120 total warnings – predominately unused imports. 4 major issues (bare `except`, invalid f-strings) to be fixed in Phase-1 hygiene.

---

## 2. MyPy `--strict`

| Sev | File:Line | Rule | Summary | Suggested Fix |
|-----|-----------|------|---------|---------------|
| 🔴 | `src/analysis/report_generator.py:429` | Syntax | `f-string: single '}' is not allowed` prevents type-checking | Correct stray `}` or escape it; rerun MyPy |

_Type-checking aborted after first syntax error. Once fixed, expect many type errors – defer to Phase 1 "100 % typed surface"._

---

## 3. Safety (dependency vulnerabilities)

Safety reports **0 confirmed CVEs** but 17 _ignored_ due to **un-pinned versions**.

| Sev | Package | Reason | Suggested Fix |
|-----|---------|--------|---------------|
| 🟠 | _All major deps_ | Versions unpinned – potential hidden CVEs | Adopt Poetry/`pip-tools`, pin versions, rerun Safety with `--ignore-unpinned-requirements=False` |

_No immediate CVE blockers, but supply-chain governance missing._

---

## 4. Semgrep (OWASP Top-10 ruleset)

| Sev | File:Line | Rule | Summary | Suggested Fix |
|-----|-----------|------|---------|---------------|
| 🔴 | `Dockerfile:12` | `dockerfile.security.missing-user` | Container runs as root | Add `USER nonroot` & adjust file permissions |
| 🟠 | `src/reports/generator.py:12` | `jinja2.autoescape.disabled` | Jinja2 env without `autoescape` (XSS risk) | `Environment(..., autoescape=True)` or `select_autoescape()` |
| 🟠 | `src/utils/cache_manager.py:28` | `insecure-hash-md5` | MD5 used for cache key – weak hash | Switch to `sha256` from `hashlib` |
| 🟠 | `src/utils/cache_manager.py:33` | `insecure-hash-md5` | Second MD5 instance | Same as above |

---

## 5. Quick Recommendations
1. **Fix syntax error** in `report_generator.py` so MyPy can scan full project.
2. **Run Ruff `--select E,F,W` in CI**; fail build on high-severity rules.
3. **Replace MD5** with SHA-256 for cache keys.
4. **Add `USER app`** (non-root) in multi-stage Dockerfile (see Task 6).
5. **Enable Jinja2 autoescaping** in report templates to prevent XSS.
6. **Pin dependency versions** and generate SBOM; rerun Safety/Trivy.

---

### Scorecard
| Domain | Status |
|--------|--------|
| Linting hygiene | 🟡 _Fair_ — many unused imports |
| Type safety | 🔴 _Fail_ — MyPy aborted |
| Dependency CVEs | 🟠 _Needs attention_ — versions unpinned |
| Security scan | 🟠 _Needs attention_ — 1 critical, 3 major |

_This report completes Task 1. Move to Task 2 – Coverage Boost once blocking issues triaged._