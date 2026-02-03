# Technical Design Document (TDD)
## CI Operational State Service (OSS) – Hệ thống quản lý trạng thái vận hành CI cho Monitoring (độc lập CMDB)

**Version:** 1.0 (Draft)  
**Date:** 2026-01-26  
**Owner:** Platform/Monitoring Team  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#executive-summary)  
2. [Goals & Non-goals](#goals--non-goals)  
3. [Context & Problem Statement](#context--problem-statement)  
4. [Definitions](#definitions)  
5. [Functional Requirements](#functional-requirements)  
6. [Non-functional Requirements](#non-functional-requirements)  
7. [Architecture Overview](#architecture-overview)  
8. [Data Model](#data-model)  
9. [State Semantics & Evaluation](#state-semantics--evaluation)  
10. [API Design](#api-design)  
11. [Core Flows](#core-flows)  
12. [Security Model](#security-model)  
13. [Operational Concerns](#operational-concerns)  
14. [Rollout Plan](#rollout-plan)  
15. [Risks & Mitigations](#risks--mitigations)  
16. [Open Questions](#open-questions)  
17. [Revision History](#revision-history)

---

## Executive Summary

CI Operational State Service (OSS) là một hệ thống **độc lập** với CMDB, chịu trách nhiệm quản lý **trạng thái** của CI phục vụ monitoring/ops/automation.

- Mỗi CI có thể có **state machine** riêng theo loại CI/nhóm CI/ứng dụng.
- OSS cung cấp:
  - quản lý **profile/rules/assignment** (cấu hình state machine) cho CI
  - nhận **state updates** (đã được một hệ thống khác xử lý từ events) và lưu **current state** + **history**
  - manual override / suppression / maintenance window
  - API query và subscription (stream/webhook) cho downstream.

---

## Goals

### Goals

- Chuẩn hoá và quản lý **operational states** cho CI theo nhiều domain (availability/health/performance…).
- Hỗ trợ profile/rules và gán profile cho CI theo selector.
- Cung cấp API query current state, history, và subscription updates.
- Đảm bảo audit đầy đủ (ai/nguồn nào đổi state, reason/evidence).
- Kiểm soát flapping (hysteresis/cooldown/TTL).

---

## Context & Problem Statement

Monitoring tạo nhiều tín hiệu (alerts/check results/events). Các hệ thống downstream (NOC dashboard, incident mgmt, automation) cần một “nguồn sự thật” về trạng thái vận hành của CI:

- Một CI có thể “down” theo availability, nhưng “degraded” theo performance.
- Có maintenance window làm trạng thái hiển thị khác với trạng thái thực tế.
- Có manual override để phục vụ điều phối vận hành.
- Cần lịch sử chuyển trạng thái để postmortem, audit, và reporting.

Do đó cần một service độc lập: OSS.

---

## Definitions

- **CI Ref**: định danh tham chiếu CI từ hệ thống ngoài (CMDB/Cloud/K8s…).  
  Format khuyến nghị: `"<source>:<id>"` (string), ví dụ: `cmdb:123`, `aws:i-abc`, `k8s:ns/pod`.
- **Operational State**: trạng thái vận hành phục vụ monitoring/ops.
- **State Domain**: “chiều trạng thái” (state dimension) để **một CI có thể có nhiều trạng thái song song** tuỳ mục tiêu sử dụng.
  - Ví dụ:
    - `availability`: `UP/DOWN/MAINTENANCE/UNKNOWN`
    - `health`: `HEALTHY/DEGRADED/UNHEALTHY`
    - `performance`: `OK/SLOW/CRITICAL`
  - Nếu tổ chức chỉ cần **1 trạng thái duy nhất/CI**, có thể “đóng cứng” domain = `operational` (nhưng tài liệu này thiết kế theo hướng **multi-domain**).
- **Profile**: “gói cấu hình trạng thái” áp dụng cho **một nhóm CI**. Profile quyết định:
  - **Domain nào được quản lý** cho nhóm CI đó (availability/health/…)
  - **State set** của từng domain (các `state_key` hợp lệ + severity/TTL/override flags)
  - **Rule/transition**: event nào sẽ map sang state nào, priority/hysteresis/cooldown ra sao
  - **Precedence/behavior**: cách ưu tiên maintenance/override, TTL hết hạn xử lý thế nào (nếu được cấu hình)
  
  Profile được **gán** vào CI qua `ci_assignments` (explicit hoặc selector). Profile nên **versioned** để thay đổi rule an toàn (activate phiên bản mới, rollback được).
- **Evidence**: “bằng chứng” (fact) giải thích **vì sao state đổi** tại một thời điểm. Evidence không phải là state; nó là dữ liệu tham chiếu phục vụ audit/debug.
  - Ví dụ evidence:
    - Alert: `{source: "prometheus", alert_name: "HostDown", alert_id: "...", labels: {...}}`
    - Check result: `{check: "ping", status: "CRIT", rtt_ms: 999, output: "..."}`
    - Ticket/incident: `{system: "itsm", ticket_id: "INC-123", url: "..."}`
    - Manual action: `{actor: "alice", action: "override", reason: "..."}`
  - Evidence nên được lưu dưới dạng `evidence_ref` (ID/URL) + snapshot tối thiểu trong `state_updates_received.payload` (hoặc `ci_state_history.reason`) tuỳ chính sách retention.

---

## Profile & Evidence (how-to)

### Profile dùng để làm gì?

Mục tiêu của Profile là để OSS **không phải hardcode** state logic cho mọi CI, mà có thể cấu hình theo nhóm:

- Ví dụ: nhóm `db-prod` có rule nghiêm hơn (chỉ cần 1 alert là `DOWN`), còn `dev` có hysteresis/cooldown lớn hơn.
- Ví dụ: `availability` của `load-balancer` có states khác `availability` của `kafka-broker` (dù cùng domain).

### Evidence đi theo luồng thay đổi trạng thái thế nào?

Khi có một **state update** được tạo bởi hệ thống xử lý events (Event Processing/Correlation):

1. Event Processing System ingest & correlate raw events (alert/check/metric/...) và quyết định **state target**.
2. OSS nhận state update và lưu `state_updates_received` (payload chứa evidence/ref).
3. Nếu state đổi, OSS ghi `ci_state_history` với:
   - `from_state_key` → `to_state_key`
   - `at`
   - `reason` (tóm tắt ngắn)
   - `evidence_ref` (trỏ về event/alert/ticket/…)

Nhờ đó khi query history, team có thể trả lời: “**CI này down lúc 10:05 vì alert HostDown firing (alert_id=...)**”.

---

## Functional Requirements

### 1) State Modeling

- Quản lý domains.
- Quản lý profile (versioned): `draft → active → deprecated`.
- Mỗi domain trong profile có:
  - state definitions: `state_key`, `label`, `severity`, `ttl_seconds`, `is_override?`
  - transition rules: match event → target state, priority, hysteresis, cooldown.

### 2) Assignment (gán profile cho CI)

- Gán theo:
  - **explicit**: danh sách CI refs
  - **selector/query**: label-based hoặc query DSL đơn giản (team/env/app/type…)
- Quy tắc ưu tiên: explicit > selector > default.
- Hỗ trợ thời gian hiệu lực `effective_from/to`.

### 3) Ingestion

### 3) Integration với Event Processing System (OSS không xử lý raw events)

- OSS **không ingest/parse/correlate** raw monitoring events.
- Một hệ thống khác (Event Processing/Correlation) sẽ:
  - ingest raw events (alerts/check results/metrics/…)
  - áp dụng rules/state machine (dựa trên profiles/assignments)
  - gửi **state updates** vào OSS để lưu trữ & phân phối.

OSS cần cung cấp:

- **Config APIs** để Event Processing System đọc cấu hình:
  - profiles/state definitions/rules
  - assignments
  - (khuyến nghị) endpoint “effective profile” theo `ci_ref` để giảm logic resolve ở phía processor.
- **State Update API** để nhận kết quả đã tính:
  - batch update
  - idempotency (theo `update_id` / `Idempotency-Key`)
  - ordering per `ci_ref` (theo `sequence` hoặc `observed_at` + conflict policy).

### 4) Evaluation

### 4) State semantics enforcement (phạm vi của OSS)

OSS có thể (tuỳ chọn) enforce một số semantics mang tính “storage-level”:

- precedence của `MAINTENANCE` / `MANUAL_OVERRIDE` so với updates thông thường
- suppression/ack (nếu OSS là nơi nhận actions)
- history/audit append-only
- TTL của current state (nếu OSS nhận `ttl_seconds` cùng update).

### 5) Query & Subscribe

- Query current state:
  - theo CI ref (all domains / 1 domain)
  - theo filter (state=DOWN, team=…, domain=…)
- Query history theo time range.
- Subscribe updates:
  - SSE/WebSocket cho UI
  - Webhook dispatcher cho downstream
  - (tuỳ chọn) channel stream nội bộ “state-updates” nếu cần fan-out lớn.

### 6) Audit

- Lưu audit cho:
  - ai (user/service account) thực hiện manual action
  - nguồn event
  - correlation id
  - evidence/links (alert id/ticket id).

---

## Non-functional Requirements

### Availability & Reliability

- Availability target: 99.9% (khuyến nghị stateless API + queue + worker).
- At-least-once delivery cho **state updates**; hệ thống phải idempotent.

### Performance (baseline targets)

- State update received → current state updated: p95 < 2s.
- Query current state: p95 < 200ms (cache + index).

### Scalability (sizing assumptions)

- CI: 100k–1M
- Event rate: 1k–50k events/s (tuỳ monitoring)
- History retention: 6–24 tháng; events raw: 30–90 ngày.

### Consistency

- Bảo toàn ordering “per CI ref” (ít nhất trong cùng domain).

---

## Architecture Overview

### Logical Architecture

```
Monitoring / Agents
        |
        |  (raw events)
        v
Upstream Systems (out of scope)
(Monitoring / Correlation / Automation)
        |
        |  (state updates + evidence refs)
        v
State API (State Update endpoint)
        |
        v
Primary DB (config + current + history + received updates)
        |
        +--> State Updates (Webhook/SSE)  [fan-out to downstream]
        |
        v
Cache (Redis) for hot current states
        |
        v
State API (Query / Admin / Actions)
```

### Components

- **Upstream Systems (external, out of scope)**
  - Nơi ingest/correlate raw events (nếu có) và/hoặc logic automation.
  - **OSS không xử lý raw events**; upstream chỉ gửi **state updates** (kèm evidence refs) vào OSS.
  - (tuỳ chọn) upstream có thể query OSS để lấy profiles/assignments/effective profile nếu upstream là nơi áp state machine.
- **Scheduler**
  - manage maintenance windows
  - generate internal events (start/end).
- **State API**
  - CRUD domains/profiles/assignments
  - query current/history
  - manual actions
  - receive state updates from upstream systems.
- **Storage**
  - Primary DB: PostgreSQL (khuyến nghị)
  - Cache: Redis
  - Optional: event store (ClickHouse/TimescaleDB) khi event raw cực lớn.

### Independence from CMDB

OSS chỉ lưu **CI Ref** và các trạng thái vận hành; không phụ thuộc schema CMDB.

Tích hợp tuỳ chọn:

- **Runtime enrichment**: UI gọi CMDB API để lấy tên/type khi hiển thị.
- **Metadata cache sync (khuyến nghị khi traffic lớn)**: job định kỳ sync CI metadata tối thiểu (display_name, type, team) về OSS để query/filter nhanh mà không gọi CMDB realtime.

---

## Tech Stack

Mục tiêu: triển khai OSS trên **VM**, ưu tiên **đơn giản vận hành**, không Kafka, nhận **state updates** qua HTTP, lưu DB + phát Webhook/SSE.

### Runtime & Framework

- **Language**: Go 1.22+
- **HTTP framework**: `gin` (phổ biến)
- **API spec**: OpenAPI 3 (generate clients nếu cần)

### Storage

- **Primary DB**: PostgreSQL 15+
  - Partition theo tháng cho `ci_state_history` và `state_updates_received`
  - Index: `(ci_ref, domain_id)`, `to_state_key`, `observed_at`
- **Cache (khuyến nghị)**: Redis 6/7
  - cache current state hot keys
  - rate limiting counters
  - webhook retry queue (nếu dùng background worker)

### Background jobs (Webhook retries / fan-out)

- **Queue (không Kafka)**: Queue exeption golang lib
  - Khuyến nghị: `asynq` (Go) cho retry/backoff/DLQ
  - Alternative: Postgres table `webhook_deliveries` + worker poll (đơn giản, ít phụ thuộc, nhưng tăng tải DB)

### Scheduler (maintenance windows)

- `robfig/cron` (cron expressions) + persistence trong Postgres
- **Leader election trên VM**: Postgres advisory lock hoặc Redis lock để chỉ 1 instance scheduler active

### AuthN/AuthZ

- **OIDC/JWT**: validate JWT, map roles theo claims
- **Service-to-service**: mTLS hoặc JWT service account

### Observability

- **Metrics**: Prometheus `/metrics` (`promhttp`)
- **Logging**: `zap` (JSON logs) + bắt buộc `request_id`, `update_id`, `ci_ref`
- **Tracing**: OpenTelemetry Go → OTLP (Tempo/Jaeger)

### Deployment trên VM

- **Process manager**: `systemd`
  - `oss-api.service`
  - `oss-worker.service` (nếu dùng asynq)
  - `oss-scheduler.service` (nếu tách riêng; hoặc embed vào api)
- **Reverse proxy**: Nginx (TLS termination, rate limit; cấu hình phù hợp cho SSE)
- **Config**: env vars + YAML/TOML (`viper`)
- **DB migrations**: `goose` hoặc `atlas`

## Data Model

### Identifier: CI Ref

Khuyến nghị dùng string key:

- `ci_ref` = `"<source>:<id>"`
- Ví dụ: `cmdb:123`

Lý do:

- độc lập nguồn CI
- dễ partition/shard/index
- mở rộng multi-source về sau.

### Core Tables (logical)

#### 1) `state_domains`

- `domain_id` (PK)
- `name` (unique) — `availability|health|performance|security|...`
- `description`

#### 2) `state_profiles`

- `profile_id` (PK)
- `name`
- `version` (int)
- `status` (`draft|active|deprecated`)
- `created_by`, `created_at`
- `updated_by`, `updated_at`

#### 3) `state_definitions`

- `profile_id` (FK)
- `domain_id` (FK)
- `state_key` (string) — ví dụ `UP|DOWN|DEGRADED|MAINTENANCE|UNKNOWN`
- `label` (string)
- `severity` (int) — 0..n
- `ttl_seconds` (nullable)
- `is_override` (bool) — true cho states kiểu maintenance/forced

#### 4) `state_rules`

- `rule_id` (PK)
- `profile_id` (FK)
- `domain_id` (FK)
- `match` (JSON/DSL) — điều kiện match event
- `target_state_key`
- `priority` (int) — cao thắng
- `hysteresis` (JSON) — `{min_occurrences, window_seconds}`
- `cooldown_seconds` (int)

#### 5) `ci_assignments`

- `assignment_id` (PK)
- `profile_id` (FK)
- `priority` (int)
- `selector_type` (`explicit_ci|label_query`)
- `selector` (JSON)
- `effective_from`, `effective_to` (nullable)

#### 6) `ci_current_states`

- PK: `(ci_ref, domain_id)`
- `state_key`
- `since` (timestamp) — bắt đầu trạng thái hiện tại
- `last_event_id` (UUID/string)
- `last_updated_at` (timestamp)
- `override_until` (nullable)
- `suppressed_until` (nullable)
- `ack_status` (nullable)

#### 7) `ci_state_history` (append-only)

- `history_id` (PK)
- `ci_ref`, `domain_id`
- `from_state_key`, `to_state_key`
- `at` (timestamp)
- `actor_type` (`system|user|service`)
- `actor_id` (nullable)
- `reason` (text)
- `evidence_ref` (nullable)
- `correlation_id` (nullable)

#### 8) `state_updates_received` (idempotency/audit)

- `update_id` (PK) — UUID hoặc id từ Event Processing System
- `source` — tên processor/system
- `ci_ref`
- `domain_id`
- `to_state_key`
- `observed_at` (timestamp) — thời điểm state được kết luận ở processor
- `received_at` (timestamp)
- `sequence` (optional) — nếu processor có sequence per `ci_ref`
- `payload` (JSON) — evidence snapshot / references
- `dedup_key` (unique per time window; optional)
- `status` (`accepted|rejected|applied|ignored|deadletter`)

---

## State Semantics & Evaluation

### State precedence (đề xuất)

1. **MAINTENANCE** (planned/unplanned)
2. **MANUAL_OVERRIDE** (force state)
3. **ALERT-derived states** (DOWN/DEGRADED/…)
4. **PASSING checks** (UP/OK)
5. **No signal / TTL expired** → UNKNOWN (hoặc STALE)

### Anti-flapping

- **Cooldown**: giới hạn frequency đổi state.
- **Hysteresis**: yêu cầu N lần “OK” trong window trước khi chuyển về UP.

### TTL / Staleness

- Với states có TTL, nếu quá TTL không nhận event mới → chuyển `UNKNOWN` (hoặc `STALE`).

### Suppression

- Suppression không nhất thiết đổi state, nhưng có thể:
  - mute notifications
  - hoặc đổi state sang `SUPPRESSED` tuỳ profile.

---

## API Design

### API Style

- REST JSON.
- Versioned: `/api/v1/...`
- Batch **state update** và batch query được hỗ trợ để giảm overhead.

### Common fields

Mọi request nên truyền:

- `X-Request-Id` (correlation)
- `Idempotency-Key` (cho state updates/actions)

### Endpoints (proposed)

#### Profiles

- `POST /api/v1/state/profiles`
- `GET /api/v1/state/profiles?status=active`
- `GET /api/v1/state/profiles/{profile_id}`
- `POST /api/v1/state/profiles/{profile_id}:activate`

#### Assignments

- `POST /api/v1/state/assignments`
- `GET /api/v1/state/assignments?ci_ref=cmdb:123`
- `DELETE /api/v1/state/assignments/{assignment_id}`

#### State updates (from upstream systems)

- `POST /api/v1/state/updates` (batch)

State update minimal schema (recommendation):

- `update_id` (required; UUID từ processor)
- `source` (processor/system name)
- `ci_ref`
- `domain` (required)
- `to_state_key` (required)
- `from_state_key` (optional; OSS có thể tự suy ra)
- `observed_at` (required)
- `ttl_seconds` (optional)
- `sequence` (optional; nếu processor đảm bảo ordering per CI)
- `evidence_ref` (optional)
- `payload` (optional; evidence snapshot)

#### Manual actions

- `POST /api/v1/state/cis/{ci_ref}/domains/{domain}:override`
- `POST /api/v1/state/cis/{ci_ref}/domains/{domain}:clearOverride`
- `POST /api/v1/state/cis/{ci_ref}/domains/{domain}:ack`
- `POST /api/v1/state/cis/{ci_ref}/domains/{domain}:suppress`

#### Query

- `GET /api/v1/state/cis/{ci_ref}` (all domains)
- `GET /api/v1/state/cis/{ci_ref}/domains/{domain}`
- `GET /api/v1/state/query?domain=availability&state=DOWN&team=abc`

#### History

- `GET /api/v1/state/cis/{ci_ref}/history?domain=availability&from=...&to=...`

#### Subscribe

- `GET /api/v1/state/stream` (SSE) — realtime state change feed
- `POST /api/v1/state/webhooks` — register webhook endpoint

---

## Core Flows

### 1) Receive state update → Persist → Notify

1. Event Processing System gửi state update (đã tính) vào OSS.
2. OSS validate + normalize `ci_ref` + check idempotency theo `update_id/Idempotency-Key`.
3. OSS áp dụng storage-level semantics (nếu bật): precedence của maintenance/override, suppression/ack.
4. Nếu state đổi:
   - update `ci_current_states`
   - append `ci_state_history`
5. Emit update ra downstream qua Webhook/SSE.

### 2) Maintenance window

- Scheduler đặt trạng thái `MAINTENANCE` (hoặc tạo “maintenance update”) cho tập CI refs → OSS coi như override theo precedence.

### 3) Manual override

- UI gọi `:override` với `until` + `reason`.
- OSS cập nhật current state và ghi history/audit (và có thể emit webhook/SSE).

---

## Security Model

### Authentication

Chọn một trong các mô hình:

- **A. Reuse ACL service**: tạo app riêng `state-mgmt` để quản lý roles/resources cho OSS.
- **B. OIDC**: validate JWT từ IdP, map roles theo claims.

### Authorization

- Resources:
  - `state_profile`, `state_assignment`, `state_query`, `state_action`
- Permissions:
  - `read`, `create`, `update`, `delete`, `act` (manual actions)
- Có thể mở rộng theo team/project (multi-tenant hoặc RBAC theo label).

### State update authentication

- Service accounts + JWT/mTLS
- HMAC signature cho sources đơn giản (optional)
- Rate limit theo source.

---

## Operational Concerns

### Observability

- Metrics:
  - state update rate, dedup rate, invalid updates
  - state change rate, flapping rate
  - query latency, cache hit rate
  - webhook delivery success/failure
- Logs:
  - structured logs kèm `request_id`, `update_id`, `ci_ref`
- Tracing:
  - correlation update received → persist → publish.

### Data retention

- `state_updates_received`: 30–90 ngày (partition theo ngày/tháng)
- `ci_state_history`: 6–24 tháng (partition theo tháng)
- `ci_current_states`: giữ lâu dài

### HA & Scaling

- API stateless scale ngang.
- OSS tập trung scaling theo API/DB/Redis + webhook dispatcher (không cần evaluator workers trong OSS).
- DB HA (managed Postgres hoặc Patroni).
- Redis HA (sentinel/cluster).

---

## Rollout Plan

### Phase 0 (MVP)

- Domain `availability`
- Ingest + current state + basic query
- Simple rules (alert firing/resolved)

### Phase 1

- Profiles/versioning + assignments
- History + manual override
- TTL + basic hysteresis

### Phase 2

- Maintenance scheduler
- Subscribe (SSE/Webhook)
- Advanced anti-flapping (cooldown)

### Phase 3

- Metadata cache sync (optional)
- Multi-domain + advanced selector
- Hardening: quotas, multi-tenant, reporting

---

## Risks & Mitigations

- **Event storm/duplicate**: idempotency, dedup key, backpressure, rate limit.
- **Phụ thuộc CMDB để hiển thị**: metadata cache sync + fallback.
- **Rule complexity & sai lệch semantics**: versioned profiles, staged rollout, test/sandbox.
- **Consistency khi scale**: partition by `ci_ref`, transactional update current+history.

---

## Open Questions

1. Scale thực tế: số CI, event/s peak?
2. Cần bao nhiêu domain? (availability/health/performance…)
3. Event Processing System sẽ là gì? (có sẵn hay cần build) và state update schema/contract?
4. AuthN/AuthZ: reuse ACL hay OIDC?
5. UI: cần UI riêng hay chỉ API cho downstream?
6. Semantics cần theo chuẩn nào? (ví dụ mapping severity P1..Pn, maintenance behavior)

---

## Revision History

| Version | Date | Author | Changes |
|--------:|:-----|:-------|:--------|
| 1.0 | 2026-01-26 | GPT-5.2 (Cursor agent) | Initial draft |

---

## Appendix A — Default State Table (áp dụng cho tất cả CI)

Mục tiêu: có một **tập trạng thái “chuẩn”** để mọi CI đều dùng được (dù CI là server, certificate, contract, employee…). OSS hỗ trợ multi-domain, nhưng để triển khai thực tế dễ dàng, khuyến nghị tối thiểu 2 domain:

### A1) Domain `availability` (runtime reachability)

Áp dụng cho CI “có vận hành/runtime” (server, network, storage, app service, k8s resources, monitoring components…).

| State key | Severity | Ý nghĩa |
|---|---:|---|
| `UP` | 0 | Đang hoạt động bình thường |
| `DEGRADED` | 1 | Hoạt động nhưng suy giảm/chập chờn (partial outage, error rate tăng, latency cao) |
| `DOWN` | 2 | Không hoạt động/không reachable/đứt dịch vụ |
| `MAINTENANCE` | 0 | Đang bảo trì (được đặt bởi scheduler hoặc manual override) |
| `UNKNOWN` | 3 | Không đủ tín hiệu/TTL hết hạn/không xác định |

### A2) Domain `lifecycle` (expiry / validity / lifecycle)

Áp dụng cho CI “không phải runtime” nhưng vẫn cần theo dõi trạng thái theo thời gian (certificate, hợp đồng, vulnerability record, account…).

| State key | Severity | Ý nghĩa |
|---|---:|---|
| `ACTIVE` | 0 | Hợp lệ/đang dùng |
| `EXPIRING` | 1 | Sắp hết hạn (có threshold, ví dụ 30/14/7 ngày) |
| `EXPIRED` | 2 | Hết hạn/không hợp lệ |
| `INACTIVE` | 1 | Không còn sử dụng/đã tắt (không nhất thiết lỗi) |
| `UNKNOWN` | 3 | Thiếu dữ liệu ngày hết hạn/không xác định |

### A3) Domain `health` (optional, when needed)

Khi cần tách “availability” (up/down) khỏi “health” (sức khoẻ nội bộ), dùng thêm domain `health`.

| State key | Severity | Ý nghĩa |
|---|---:|---|
| `HEALTHY` | 0 | Sức khoẻ tốt |
| `DEGRADED` | 1 | Sức khoẻ giảm |
| `UNHEALTHY` | 2 | Không khoẻ (nhưng có thể vẫn UP) |
| `UNKNOWN` | 3 | Không xác định |

Ghi chú:

- OSS có thể chạy chỉ với `availability` (Phase 0), sau đó mở rộng thêm `lifecycle/health` mà không phá vỡ dữ liệu (do thiết kế multi-domain).

---

## Appendix B — Default Profile Mapping cho các CI Types (danh sách bạn cung cấp)

Mục tiêu: có “bảng gán profile” để toàn bộ CI types đều có trạng thái theo dõi, nhưng không ép mọi CI phải có logic giống nhau.

### B1) Catalog profile mặc định

- **`profile.runtime.default`**
  - **Domains**: `availability` (bắt buộc), `health` (tuỳ chọn)
  - **Áp dụng cho**: các CI có runtime/monitoring signals (host, network, app service, k8s…)
- **`profile.lifecycle.default`**
  - **Domains**: `lifecycle`
  - **Áp dụng cho**: certificate/contract/account/vulnerability record… (theo dõi theo ngày, không nhất thiết “up/down”)
- **`profile.passive.default`**
  - **Domains**: (không bắt buộc) hoặc chỉ `lifecycle` rất nhẹ
  - **Áp dụng cho**: các CI “tham chiếu/quản trị” (role, org unit, topology…) nếu không muốn phát sinh signal monitoring

### B2) Mapping theo CI type (theo nhóm)

> Cách triển khai: dùng `ci_assignments.selector_type = label_query` với điều kiện `ci_type in (...)` hoặc `ci_type_prefix`/labels (tuỳ bạn sync metadata).

#### Nhóm Runtime (gán `profile.runtime.default`)

- **Compute/Virtualization**
  - `hypervisor_host`, `virtual_machine`, `virtualization_platform`, `physical_server`, `server`
- **Kubernetes**
  - `kubernetes_cluster`, `kubernetes_namespace`, `kubernetes_node`, `kubernetes_service_resource`, `kubernetes_raw`
- **Network**
  - `load_balancer`, `firewall`, `router`, `switch`, `port_switch`, `port_group`, `vswitch_dvs`, `tunnel_channel`, `circuit`, `internet_connection_channel`, `network_interface`, `nic`
- **Storage**
  - `physical_san_system`, `san_volume_lun`, `physical_nas_system`, `nas_shared`
- **IPAM**
  - `ipam`, `ipam_scope`, `ipam_subnet`, `ipam_address`, `ip_planning`
- **App/Service**
  - `app`, `application_service`, `bussiness_service`, `product`, `service_version`, `software`, `cache`, `database`, `queue`, `monitoring`
- **Ingress/Proxy**
  - `nginx_forward`, `nginx_ingress`
- **Security runtime controls**
  - `security_waf`, `security_ips`, `firewall_rule`
- **DCIM runtime-ish**
  - `datacenter`, `dcim_region`, `dcim_idc`, `dcim_server_room`, `dcim_rack`, `rack_device`, `pdu`

#### Nhóm Lifecycle (gán `profile.lifecycle.default`)

- **Certificates / Validity**
  - `certificate`
- **Contracts**
  - `service_support_contract`, `equipment_supply_contract`
- **Vulnerability & Security reporting**
  - `vulnerability`, `report_security`
- **Accounts**
  - `dba_user`

#### Nhóm Passive/Reference (gán `profile.passive.default` hoặc `profile.lifecycle.default` nếu muốn track ACTIVE/INACTIVE)

- `role`, `department`, `organizational_unit`, `employee`, `office`, `position`
- `topology`, `domain` (DNS domain nếu chỉ muốn quản trị, không monitor runtime)
- `approval_permissions_matrix`, `application_role_matrix`, `employee_accesscontrol`
- `Environments`

#### Nhóm “Jobs/Processes” (tuỳ cách bạn monitor)

Các CI loại job có thể coi là runtime (nếu có check/heartbeat), hoặc lifecycle (nếu chỉ track trạng thái theo lịch):

- `job_backup`, `job_moveonoff`, `job_moveonoff_detail`, `synchronize`

### B3) CI types chưa rõ semantics (cần bạn xác nhận)

Các type sau cần quyết định thuộc nhóm nào (runtime/lifecycle/passive) và domain nào là đúng:

- `vlan` (thường passive/reference hoặc lifecycle)
- `nagios_host`, `nagios_service` (thường runtime)
- `Trellix`, `Splunk_Forwarder` (agent/runtime)
- `example_ci`, `base_ci`, `quang_dang`, `116` (alias “No alias”) — cần định nghĩa lại mục đích

### B4) Nguyên tắc chung để “bảng trạng thái” phù hợp mọi CI

- Nếu CI có tín hiệu monitoring theo thời gian (heartbeat/check/alert): ưu tiên `availability` (và thêm `health` nếu cần).
- Nếu CI có “hạn dùng/validity/tuân thủ”: dùng `lifecycle`.
- Nếu CI chỉ để phân loại/quản trị và không muốn noise: gán `passive` (hoặc chỉ `lifecycle` với `ACTIVE/INACTIVE`).



