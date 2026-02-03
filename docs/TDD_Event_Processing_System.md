# Technical Design Document (TDD)
## Event Processing System (EPS) – Nhận log / Change Request / Alert và chuẩn hoá event + xác định CI bị ảnh hưởng (impact)

**Version:** 1.0 (Draft)  
**Date:** 2026-01-26  
**Owner:** Platform / Ops Engineering  
**Scope:** Thiết kế kỹ thuật tổng quan (không code), triển khai độc lập với CMDB/OSS

---

## Table of Contents

1. [Executive Summary](#executive-summary)  
2. [Goals](#goals)  
3. [Non-goals](#non-goals)  
4. [Definitions](#definitions)  
5. [Inputs & Event Sources](#inputs--event-sources)  
6. [Core Responsibilities](#core-responsibilities)  
7. [Architecture Overview](#architecture-overview)  
8. [Processing Pipeline](#processing-pipeline)  
9. [CI Correlation & Impact Analysis](#ci-correlation--impact-analysis)  
10. [Outputs](#outputs)  
11. [Data Model](#data-model)  
12. [API & Integration Contracts](#api--integration-contracts)  
13. [Reliability, Backpressure, Idempotency](#reliability-backpressure-idempotency)  
14. [Security & Audit](#security--audit)  
15. [Observability](#observability)  
16. [Deployment (VM, Golang)](#deployment-vm-golang)  
17. [Phased Rollout](#phased-rollout)  
18. [Open Questions](#open-questions)

---

## Executive Summary

EPS là hệ thống **nhận và xử lý tín hiệu vận hành** từ các nguồn bên ngoài (log lỗi, alerts, change requests, security events…). EPS chịu trách nhiệm:

- Chuẩn hoá (normalize) events về schema thống nhất
- Correlate/dedup/group events thành incident candidates
- Map events/incident → **CI bị ảnh hưởng** (1 CI hoặc nhiều CI)
- Tính **impact/blast radius** dựa trên CMDB topology/relationships
- Xuất **normalized events + CI mappings + impact sets** để các hệ thống downstream (Orchestrator/State management/Reporting) tiêu thụ

**Lưu ý boundary**:

- **CMDB** là core data system-of-record (CI types/attrs/relations).
- **OSS** là state store (current/history/notify) và **không xử lý raw events**.
- EPS **không thay thế** log platform/alert platform/ITSM; EPS chỉ ingest/correlate/enrich và xuất **normalized + impact artifacts**.

---

## Goals

- Hợp nhất nhiều nguồn tín hiệu thành event model thống nhất.
- Xác định chính xác `ci_ref` bị ảnh hưởng và danh sách CIs liên quan (impact set).
- Sinh artifacts (normalized event, incident group, CI mapping, impact set) có audit/evidence rõ ràng, idempotent.
- Hỗ trợ correlation theo time window để giảm noise (dedup, grouping, suppression).
- Cho phép rule-based mapping/correlation có versioning và rollout an toàn.

---

## Non-goals

- Không lưu/replace dữ liệu CMDB (types/attributes/relations/topology).
- Không là system-of-record cho ticket/change (ITSM vẫn là nguồn chuẩn).
- Không là hệ thống UI chính (có thể có UI tối thiểu cho ops/debug).
- Không là nơi lưu embeddings/RAG (thuộc Knowledge Base).

---

## Definitions

- **Event**: tín hiệu thô/chuẩn hoá từ nguồn (log/alert/CR/security).
- **Normalized Event**: event sau normalize về schema chung của EPS.
- **Incident Group**: nhóm các events liên quan (dedup/correlation) trong một window.
- **CI Ref**: định danh CI chuẩn, ví dụ `cmdb:<ci_id>`.
- **Impact Set**: tập CI bị ảnh hưởng trực tiếp/gián tiếp (blast radius).
- **Evidence**: bằng chứng đính kèm output (alert id/log query/CR id/link).
- **Artifact**: output của EPS để downstream tiêu thụ (normalized event, incident group, CI mapping, impact set).

---

## Inputs & Event Sources

### 1) Logs / Errors

- Nguồn: ELK/OpenSearch, Splunk, Loki, application error streams, syslog.
- Hình thức ingest:
  - webhook (push) từ log alerting
  - polling (scheduled queries) – hạn chế, chỉ dùng khi bắt buộc
  - message stream (tuỳ tổ chức; không bắt buộc Kafka).

### 2) Alerts / Monitoring

- Nguồn: Prometheus Alertmanager, Nagios, Zabbix, custom monitoring.
- Ingest: webhook.

### 3) Change Requests (CR) / ITSM

- Nguồn: ServiceNow, Jira Service Management, OTRS, custom.
- Ingest:
  - webhook khi CR tạo/approve/start/end
  - polling fallback.

### 4) Security Events (optional)

- IDS/WAF/EDR, vulnerability scanners, SIEM.

---

## Core Responsibilities

1. **Normalize**: biến nhiều schema → 1 schema chuẩn.
2. **Enrich**: gắn metadata (env/service/team) bằng cách query CMDB hoặc cache.
3. **Correlate**:
   - dedup theo fingerprint
   - group theo time window + similarity
   - suppression rules (maintenance, known noisy signatures)
4. **CI Mapping**: xác định `ci_ref` liên quan (direct + inferred).
5. **Impact Analysis**: mở rộng từ CI trực tiếp → impact set theo topology.
6. **Decision**:
   - incident severity mapping (metadata phục vụ grouping/triage, **không phải state**)
7. **Outputs**:
   - normalized events + incident groups
   - CI mappings (confidence + evidence)
   - impact sets (blast radius + derivation evidence)

---

## Architecture Overview

```
External Sources (Logs / Alerts / CR / Sec)
          |
          |  (webhooks / connectors)
          v
EPS Ingest API  --->  Normalize + Validate
          |
          v
Correlation Engine (dedup/group/suppress)
          |
          v
CI Correlation + Impact Analyzer  <---->  CMDB Query Adapter (read-only)
          |
          v
Decision Engine (severity + artifact generation)
          |
          +--> Artifacts Store / APIs (normalized + mappings + impact)
                     |
                     +--> Downstream consumers (Orchestrator / State Mgmt / Reporting)
```

---

## Processing Pipeline

### Step 0 — Ingest & authentication

- Verify source identity (JWT/mTLS/HMAC).
- Apply rate limiting & payload size limits.
- Assign `event_id` (UUID) nếu nguồn không cung cấp.

### Step 1 — Normalize

Convert payload về **NormalizedEvent** (JSON):

- `normalized_event_id`
- `source_type`: `log|alert|change_request|security`
- `source_name`: `splunk|loki|alertmanager|servicenow|...`
- `observed_at`, `received_at`
- `severity` (normalized scale, ví dụ 0..5)
- `title`, `message`
- `fingerprint` (dedup key)
- `tags/labels` (env, service, team, region…)
- `raw_ref` (link tới nguồn: alert id, log query url, CR id…)
- `candidate_ci_hints` (hostname/ip/service name/namespace…)

### Step 2 — Correlation / Dedup / Grouping

- Dedup theo `fingerprint` trong window (ví dụ 5–15 phút).
- Grouping theo:
  - cùng service/env/team
  - cùng signature (error type)
  - proximity time
  - shared CI hints
- Output: **IncidentGroup**.

### Step 3 — Enrichment

- Bổ sung metadata bằng CMDB (read-only):
  - map hostname/ip → `ci_ref`
  - map service/env/team → candidate CIs
  - lấy topology neighbors nếu cần.

### Step 4 — CI mapping

- Tạo danh sách `directly_affected_cis` (confidence scored).
- Nếu mapping mơ hồ, giữ nhiều candidate và defer decision theo policy:
  - prefer highest confidence
  - require manual confirmation
  - emit “UNKNOWN_CI_MAPPING” (internal) để xử lý.

### Step 5 — Impact analysis (blast radius)

- Từ CI trực tiếp → mở rộng impact set theo topology (CMDB relations), có rules:
  - depth limit (level=1..N)
  - relation type filters (depends_on, hosted_on, connected_to…)
  - directionality
  - stop conditions (boundary by environment/team/service).

### Step 6 — Decision & outputs

- Tính `incident_severity` (chỉ metadata phục vụ triage/grouping, không phải state).
- Persist artifacts:
  - normalized events
  - incident groups
  - CI mappings + confidence
  - impact sets + derivation evidence
- Downstream systems (out of scope) sẽ quyết định:
  - cập nhật state (nếu có) hoặc phát cảnh báo/automation.

---

## CI Correlation & Impact Analysis

### 1) CI correlation strategies (theo độ ưu tiên)

1. **Direct CI Ref**: event chứa `cmdb:<id>` (best).
2. **Unique attributes**:
   - hostname / fqdn
   - instance_id
   - ip address (qua IPAM)
3. **Service mapping**:
   - `service_name` → group of CIs (app/service topology)
4. **Topology inference**:
   - event on a component implies impact upstream/downstream by relation rules.
5. **CR-based mapping**:
   - CR chứa CI list / service scope / change plan → map sang CIs.

### 2) Confidence scoring (recommended)

Mỗi mapping ra `(ci_ref, confidence, evidence)`:

- direct ci_ref: 1.0
- exact unique match: 0.9
- attribute fuzzy match: 0.6–0.8
- topology inference only: 0.4–0.6

Thresholds:

- ≥0.8: auto-apply
- 0.6–0.8: apply với “low confidence” flag
- <0.6: require manual review / do not update state (policy quyết định)

### 3) Blast radius

EPS tạo impact set theo rule, ví dụ:

- Server DOWN → impact app services hosted_on server (level=1)
- App service degraded → impact business service depends_on (level=1..2)

EPS phải attach evidence: “impact derived via relation X from CI Y”.

---

## Outputs

EPS tạo ra các output “chuẩn hoá + impact” để downstream tiêu thụ:

1. **Normalized Events**
   - schema thống nhất + raw_ref + fingerprint + tags
2. **Incident Groups**
   - dedup/correlation theo window
   - summary + severity metadata + status (open/closed)
3. **CI Mappings**
   - `{ci_ref, confidence, mapping_evidence}` cho từng event/group
4. **Impact Sets**
   - danh sách CI bị ảnh hưởng trực tiếp/gián tiếp
   - derivation evidence: topology path / relation types / depth

---

## Data Model

### Core entities (logical)

- `normalized_events`
  - store normalized payload + fingerprint + raw_ref + tags
- `incident_groups`
  - group id, time window, summary, severity, status (open/closed)
- `event_group_links`
  - mapping event → group
- `ci_mappings`
  - group_id/event_id → ci_ref + confidence + mapping_evidence
- `impact_sets`
  - group_id → impacted ci_refs + derivation evidence
- `artifacts_outbox` (optional)
  - artifacts to deliver to downstream (webhook/pull index) theo outbox pattern

**Retention** (recommendation):

- normalized events: 7–30 ngày
- incident groups: 30–180 ngày
- mappings/impact: 30–180 ngày
- outbox: 7–30 ngày (hoặc until delivered + archived)

---

## API & Integration Contracts

### 1) Ingest APIs (external → EPS)

- `POST /api/v1/eps/ingest/log`
- `POST /api/v1/eps/ingest/alert`
- `POST /api/v1/eps/ingest/change-request`

Common requirements:

- `X-Request-Id`
- idempotency key (optional)
- strict schema validation per source type

### 2) CMDB adapter (EPS → CMDB)

Read-only APIs:

- CI lookup by unique attributes (hostname/ip/instance_id)
- topology query (neighbors by relation type, depth)
- service→CI mapping (nếu có)

### 3) OSS integration (EPS → OSS)

EPS **không gửi state updates** và **không phát cảnh báo**.

Nếu có hệ thống State Management/OSS trong ecosystem, nó sẽ nhận state updates từ hệ thống khác (out of scope).

### 4) Orchestrator integration (EPS → Orchestrator)

Optional (khuyến nghị nếu muốn A2A trigger):

- publish incident group updates (webhook) hoặc Orchestrator pull via API:
  - `GET /api/v1/eps/incidents?status=open`
  - `GET /api/v1/eps/incidents/{group_id}/impact`

---

## Reliability, Backpressure, Idempotency

- **Outbox pattern (optional)**: persist artifacts cần push cho downstream, gửi async; đảm bảo không mất dữ liệu khi EPS restart.
- **Idempotency**:
  - normalized_event_id stable by fingerprint+time bucket
  - incident_group_id/fingerprint stable theo (fingerprint + time window) tuỳ rule
- **Backpressure**:
  - rate limit ingest
  - bounded queues
  - shed load policy (drop low priority / sample logs).
- **Replay**:
  - có thể replay events trong time range để debug (nếu retention cho phép).

---

## Security & Audit

- Authn: mTLS/JWT/HMAC per source.
- Authz: allowlist sources + per-endpoint permissions.
- Audit: log mọi decision (group_id, rule_version, mapping confidence, impacted CI list).
- PII/Sensitive logs: redaction before persistence (policy-based).

---

## Observability

- Metrics:
  - ingest rate per source
  - dedup ratio, group rate
  - mapping confidence distribution
  - outbox backlog, downstream delivery success/failure (nếu có push)
  - processing latency p50/p95
- Logs:
  - structured logs with `request_id`, `normalized_event_id`, `group_id`, `ci_ref`
- Tracing:
  - ingest → correlation → mapping → impact → persistence (→ downstream delivery nếu có)

---

## Tech Stack (VM, Golang)

### Runtime & Framework

- **Language**: Go 1.22+
- **HTTP framework**: `gin`
- **Config**: env vars + file (YAML/TOML) với `viper`
- **DB migrations**: `goose` hoặc `atlas`

### Data layer

- **Primary DB**: PostgreSQL 15+
  - tables: `normalized_events`, `incident_groups`, `event_group_links`, `ci_mappings`, `impact_sets`
  - retention/partition:
    - `normalized_events`: partition theo ngày/tháng (tuỳ volume)
    - `incident_groups`/`impact_sets`: partition theo tháng (tuỳ retention)
- **Cache (optional)**: Redis 6/7
  - dedup window (fingerprint)
  - rate limit counters
  - (optional) queue cho outbox nếu EPS cần push artifacts downstream

### CMDB integration

- **Protocol**: REST (read-only)
- **Client**: timeout + retry/backoff + circuit breaker (khuyến nghị)
- **Local cache**: TTL cache cho lookup (hostname/ip/service → ci_ref) để giảm tải CMDB

### Background jobs (optional)

Nếu EPS cần deliver artifacts (webhook) theo outbox pattern:

- **Queue**: Redis-backed queue
  - khuyến nghị: `asynq` (retry/backoff/DLQ)
  - alternative: poll DB outbox (đơn giản, nhưng tăng tải DB)

### Observability libraries

- **Metrics**: Prometheus `promhttp`
- **Logging**: `zap` (JSON logs)
- **Tracing**: OpenTelemetry Go (OTLP)

---

## Deployment (VM, Golang)

Khuyến nghị stack (VM, Go):

- Go 1.22+, HTTP `gin`
- PostgreSQL 15+ (partition history/outbox nếu cần)
- Redis 6/7 (cache + optional queue)
- systemd services:
  - `eps-api.service`
  - `eps-worker.service` (correlation/decision/outbox sender)
- Nginx reverse proxy (TLS termination)

---

## Phased Rollout

1. **Phase 0**: ingest alerts + direct CI mapping + impact set (level=1).
2. **Phase 1**: log ingestion + correlation + confidence scoring.
3. **Phase 2**: CR ingestion + CI scoping (CI set impacted by change).
4. **Phase 3**: topology-based blast radius + advanced grouping + policy/approvals hooks (handoff to Orchestrator).

---

## Open Questions

1. Nguồn log/alert/CR cụ thể là gì (Splunk/ELK/Loki, Alertmanager, ServiceNow/Jira…)?
2. Quy tắc mapping CI: hiện có unique keys nào trong CMDB (hostname, instance_id, ip, service_id…)?
3. Blast radius: relation types nào là “impactful” và depth tối đa?
4. State domains bắt buộc ở giai đoạn đầu (availability vs lifecycle vs health)?
5. Policy khi mapping confidence thấp: auto-apply hay require manual review?
6. Retention & data sensitivity (log PII) yêu cầu mức nào?


