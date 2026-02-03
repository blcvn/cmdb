# System Design (Overview)
## CMDB Ecosystem theo hướng A2A (Agent-to-Agent) cho Ops + AI

**Version:** 1.0 (Draft)  
**Date:** 2026-01-26  
**Owner:** Platform / Ops / AI Enablement  
**Scope:** Tổng quan kiến trúc – không đi vào code/implementation chi tiết

---

## 1) Executive Summary

Thiết kế một hệ sinh thái xoay quanh **CMDB (Core Data)**, với các hệ thống vệ tinh để:

1. **Knowledge Base** phục vụ RAG/tra cứu (semantic retrieval, runbooks, docs, history).
2. **Event Processing System** nhận & xử lý tín hiệu từ hệ thống ngoài (log lỗi, change request, alert, security events…).
3. **CI Operational State Service (OSS)** quản lý trạng thái CI theo thời gian (current + history + notify), **không xử lý raw events**.
4. **Agent Orchestrator** phối hợp/plan/execute usecase (A2A) giữa các hệ thống theo quy trình vận hành cụ thể.

Mục tiêu: tách trách nhiệm rõ ràng, giảm coupling, tạo nền tảng tự động hoá + AI-assisted ops mà vẫn đảm bảo governance/audit.

---

## 2) “A2A” ở đây nghĩa là gì? (nhấn mạnh Agent-to-Agent)

Trong tài liệu này, **A2A** được hiểu **trọng tâm là Agent-to-Agent**:

- **Agent-to-Agent**: nhiều “agent” (tác nhân) đại diện capability của từng hệ thống (CMDB agent, KB agent, Event agent, State agent…) **giao tiếp với nhau** qua một cơ chế điều phối và các message/contract chuẩn.
- **App-to-App** chỉ là tầng kỹ thuật bên dưới: agent gọi API/stream của app tương ứng, nhưng **logic usecase** được biểu diễn như “cuộc hội thoại/phiên làm việc giữa các agents”.

**Nguyên tắc**:

- Hệ thống lõi không “biết” logic usecase; logic nằm ở Orchestrator/Agents.
- Dữ liệu chuẩn hoá và quyền truy cập được quản trị tập trung (RBAC/ABAC + audit).

### 2.1 Agent model (chuẩn hoá để A2A vận hành ổn định)

Mỗi agent nên có:

- **Capability contract**: danh sách hành động (tools) + schema I/O + error codes.
- **Policy guardrails**: hành động nào chỉ “read”, hành động nào “write”, khi nào cần approval.
- **Idempotency & correlation**: mọi lệnh phải có `request_id`/`correlation_id`.
- **Evidence & citations**: agent khi đưa ra quyết định/hành động cần đính kèm evidence (từ KB/EPS/OSS/CMDB).

### 2.2 Orchestrator là gì trong A2A?

- Orchestrator đóng vai trò **Planner/Router/Supervisor**:
  - tiếp nhận intent hoặc trigger
  - chọn agents phù hợp
  - điều phối thứ tự gọi agents (plan)
  - thu thập evidence, áp policy, và commit actions
- Orchestrator **không thay agent làm domain logic**, mà đảm bảo “cuộc hội thoại A2A” có kiểm soát, có audit, và có thể replay.

---

## 4.1 A2A Interaction Pattern (recommended)

Khuyến nghị chuẩn hoá thành 2 lớp message:

- **Intent/Task** (Orchestrator → Agent): “hãy làm X với input Y dưới policy Z”
- **Result/Artifact** (Agent → Orchestrator/Agent khác): trả về output + evidence + next suggestions

Tối thiểu mỗi message nên có:

- `request_id`, `correlation_id`
- `actor` (user/service)
- `target` (`ci_ref`, service, env…)
- `action`, `input`, `output`
- `evidence_refs` (links/ids)
- `decision_log` (ngắn, phục vụ audit)

---

## 3) Các hệ thống & trách nhiệm (Responsibilities)

### 3.1 CMDB (Core Data)

- **Nguồn dữ liệu chuẩn (system-of-record)** cho:
  - CI, CI types, attributes, relationships, topology
  - ownership/team/env labels (nếu có)
- **API**: CRUD, search, relationship, history, permissions
- **Tích hợp**:
  - xuất event “CMDB change” (tạo/sửa/xoá CI, quan hệ) cho downstream
  - cung cấp “CI Ref” chuẩn: ví dụ `cmdb:<ci_id>` cho các hệ thống vệ tinh.

### 3.2 Knowledge Base (KB) cho RAG / Tra cứu

- Thu thập tri thức từ:
  - docs/runbooks, postmortem, SOP
  - ticket/incident notes, change record summaries
  - CMDB metadata (một phần) để enrich retrieval
  - state history / event summaries (một phần)
- Chức năng:
  - indexing (text + metadata), semantic search, chunking
  - retrieval API cho RAG
  - governance: versioning nguồn, citations, retention

### 3.3 Event Processing System (EPS)

- **Ingest & normalize** raw events:
  - alerts, logs, traces-derived incidents, change requests, security events
- **Correlation & enrichment**:
  - gắn CI ref từ CMDB (service mapping, topology traversal)
  - dedup, grouping, severity mapping, suppression rules
- **Output**:
  - tạo **normalized event** và/hoặc **state update** (kết luận trạng thái mục tiêu)
  - phát event cho Orchestrator và/hoặc gửi state update sang OSS.

### 3.4 CI Operational State Service (OSS)

- Nhận **state updates** (từ EPS hoặc upstream systems khác) và:
  - cập nhật **current state** theo domain
  - lưu **state history** (append-only) + audit + evidence_ref
  - phát **notify** (webhook/SSE) + query API
- OSS **không xử lý raw events**, không làm correlation.

### 3.5 Agent Orchestrator (A2A Layer)

- Vai trò:
  - nhận “intent” (operator request / automation trigger / EPS event)
  - lập plan theo usecase
  - gọi các agents để thực thi (query CMDB, retrieve KB, create change, update state, notify…)
  - ghi audit trail, guardrails (policy checks)
- Agents điển hình:
  - **CMDB Agent**: search CI, traverse topology, update CI metadata (nếu được phép)
  - **KB Agent**: retrieve context, generate answer with citations
  - **EPS Agent**: query incidents/groups, ack/suppress, push normalized outputs
  - **State Agent**: query current/history, set override/maintenance, subscribe changes
  - **ITSM/Change Agent** (tuỳ): tạo CR/INC, cập nhật trạng thái ticket
  - **Automation Agent** (tuỳ): chạy runbook, kick off pipeline, execute remediation.

---

## 4) Kiến trúc tổng thể (High-level Architecture)

```
            +----------------------+
            |      Users / Ops     |
            |  Portal / Chat / UI  |
            +----------+-----------+
                       |
                       v
              +-------------------+
              | Agent Orchestrator|
              | (A2A Planner/Exec)|
              +--+-----+-----+----+
                 |     |     |
      retrieve   |     |     |  state query/notify
      context    |     |     v
                 |     |   +----------------------+
                 |     |   | CI State Service     |
                 |     |   | (OSS)                |
                 |     |   +----------+-----------+
                 |     |              ^
                 |     |              | state updates
                 |     v              |
                 |  +-----------------+-----+
                 |  | Event Processing System|
                 |  | (EPS: ingest/correlate)|
                 |  +-----------+-------------+
                 |              ^
                 |              | raw events
                 v              |
         +------------------+   |
         | Knowledge Base   |   |
         | (RAG / Search)   |   |
         +------------------+   |
                                |
                         +------+------+
                         | External Sys |
                         | Alert/Log/CR |
                         +-------------+

              +------------------+
              | CMDB (Core Data) |
              +------------------+
       (Queried/enriched by EPS/Orchestrator/KB)
```

---

## 5) Data ownership & identifiers

### 5.1 Ownership

- **CMDB**: ownership của CI model (types/attrs/relations).
- **EPS**: ownership của raw event processing + correlation + incident grouping.
- **OSS**: ownership của **operational state timeline** (current + history + notify).
- **KB**: ownership của embeddings/index/chunks + provenance.
- **Orchestrator**: ownership của usecase logic, policy, execution audit.

### 5.2 CI Identifier (CI Ref)

Chuẩn hoá `ci_ref` để các hệ thống nói chuyện thống nhất:

- Format: `cmdb:<ci_id>`
- (tương lai) multi-source: `aws:<id>`, `k8s:<ns>/<name>`… nhưng phải mapping về CI trong CMDB hoặc “virtual CI”.

---

## 6) Integration contracts (API/Events)

### 6.1 CMDB → EPS / KB / Orchestrator

- **CMDB Change Feed** (khuyến nghị):
  - CI create/update/delete
  - relationship changes
  - important attribute updates (owner/env/service)
- Mục đích:
  - EPS cập nhật mapping correlation
  - KB re-index nguồn liên quan
  - Orchestrator re-evaluate automation rules.

### 6.2 EPS → OSS

- **State update**:
  - `{update_id, source, ci_ref, domain, to_state_key, observed_at, evidence_ref, payload}`
- EPS chịu trách nhiệm logic chuyển raw events → state conclusion.

### 6.3 OSS → Downstream / Orchestrator

- Webhook/SSE:
  - phát “state changed” events
  - Orchestrator có thể subscribe để kích hoạt usecase remediation/notification.

### 6.4 Orchestrator ↔ KB

- Retrieval API:
  - `query(text, filters={ci_ref, service, env, time_range}) → chunks + citations`

---

## 7) Use cases tiêu biểu (end-to-end)

### UC1: Alert → correlate → update state → auto-remediate

1. External alert → EPS ingest.
2. EPS correlate: tìm `ci_ref` qua CMDB mapping/topology.
3. EPS kết luận state: `availability=DOWN` cho `cmdb:123`.
4. EPS gửi state update → OSS.
5. OSS phát webhook “state changed” → Orchestrator.
6. Orchestrator:
   - query CMDB (context/topology/owner)
   - retrieve KB (runbook)
   - execute automation (restart/rollback) (nếu policy cho phép)
   - cập nhật ticket/notify.

### UC2: Change Request planned → maintenance window

1. ITSM/CR event → EPS hoặc Orchestrator nhận trigger.
2. Orchestrator tạo maintenance window cho CI set (từ CMDB topology).
3. OSS set `MAINTENANCE` trong thời gian change.
4. Khi change kết thúc: clear maintenance, OSS emit update.

### UC3: Tra cứu nhanh “tại sao CI degraded?”

1. User hỏi Orchestrator.
2. Orchestrator query OSS: current + recent history + evidence_ref.
3. Orchestrator retrieve KB: runbook + postmortem tương tự.
4. Trả lời có citations + đề xuất hành động.

---

## 8) Security, Governance, Audit

- **Identity**: SSO/OIDC.
- **Authorization**:
  - CMDB RBAC/ABAC theo app/team/resource.
  - OSS quyền theo domain/CI scope.
  - KB quyền theo nguồn tri thức (doc ACL).
  - Orchestrator enforce policy (deny-by-default cho actions).
- **Audit**:
  - mọi action từ Orchestrator phải có `request_id`, actor, approvals (nếu cần)
  - OSS lưu history append-only + evidence refs
  - EPS lưu event lineage/correlation graph.

---

## 9) Reliability & Scaling (high level)

- CMDB: core DB + caching; ưu tiên consistency.
- EPS: scale theo ingest rate; cần backpressure và retry.
- OSS: write-heavy (updates) + read-heavy (query); partition history.
- KB: index + vector store; batch ingestion, rebuild pipelines.
- Orchestrator: stateless execution + durable workflow store (nếu usecase dài).

---

## 10) Deployment topology (VM-friendly)

Khuyến nghị tách service theo VM/cluster nhỏ:

- `cmdb` (existing)
- `kb-service` (index + retrieval)
- `eps-service` (ingest + correlation)
- `oss-service` (state store + notify)
- `orchestrator-service` (A2A)

Mỗi service:

- systemd + reverse proxy (Nginx)
- TLS everywhere
- centralized logs/metrics/tracing.

---

## 11) Phased rollout

1. **Phase 0**: OSS + EPS minimal contract (state updates) + basic Orchestrator subscribe.
2. **Phase 1**: CMDB change feed + EPS correlation improvements + KB retrieval for runbooks.
3. **Phase 2**: A2A usecases (auto-remediate) với policy/approvals.
4. **Phase 3**: Expand domains, advanced governance, reporting, multi-tenant (nếu cần).

---

## 12) Open questions (để chốt design)

1. A2A agents sẽ chạy ở đâu: embedded trong Orchestrator hay “remote agents” (service riêng) theo từng domain?
2. EPS output: chỉ gửi **state updates** hay cũng cần publish **normalized events / incident groups** cho agents khác consume?
3. KB sources cụ thể: docs nội bộ, ticket system nào, log platform nào? (và ACL/citations yêu cầu mức nào)
4. Chính sách approvals cho automation: usecase nào auto, usecase nào cần approve? (ai approve, timeout, rollback)
5. Multi-domain states: domain nào là must-have trong giai đoạn đầu? (availability vs lifecycle vs health)


