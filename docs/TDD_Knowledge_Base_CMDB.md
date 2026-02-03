# Technical Design Document (TDD)
## Knowledge Base (KB) cho CMDB ecosystem — Runbook / RCA / Standard Changes / Docs + Search + RAG

**Version:** 1.0 (Draft)  
**Date:** 2026-01-27  
**Owner:** Platform / SRE / Ops Engineering  
**Scope:** Thiết kế kỹ thuật tổng quan (không code), tích hợp với CMDB hiện tại + ecosystem (EPS/OSS/ITSM)

---

## Table of Contents

1. [Executive Summary](#executive-summary)  
2. [Goals](#goals)  
3. [Non-goals](#non-goals)  
4. [Actors & Use cases](#actors--use-cases)  
5. [Definitions](#definitions)  
6. [Architecture Overview](#architecture-overview)  
7. [Core Responsibilities](#core-responsibilities)  
8. [Data Model](#data-model)  
9. [Workflows](#workflows)  
10. [Search & Retrieval (BM25 + Vector + RAG)](#search--retrieval-bm25--vector--rag)  
11. [API & Integration Contracts](#api--integration-contracts)  
12. [Security, Permissions, Audit](#security-permissions-audit)  
13. [Reliability, Idempotency, Retention](#reliability-idempotency-retention)  
14. [Observability](#observability)  
15. [Deployment Options](#deployment-options)  
16. [Phased Rollout](#phased-rollout)  
17. [Open Questions](#open-questions)

---

## Executive Summary

Trong CMDB ecosystem, **Knowledge Base (KB)** là nơi lưu và vận hành tri thức vận hành (runbook, SOP, RCA, troubleshooting guides, standard change templates, postmortems…) và cung cấp:

- **Search** (full-text + faceted) để tìm nhanh tri thức theo CI/service/team/env.
- **Suggestion** theo ngữ cảnh (incident/change/alert) dựa trên CMDB topology + metadata.
- **RAG (optional)**: semantic retrieval + trả lời có trích dẫn nguồn (citations) cho ops, thay vì “chatbot đoán”.

Boundary khuyến nghị:

- **CMDB**: system-of-record cho CI/types/attrs/relations/history.  
- **Event Processing System (EPS)** (optional): ingest/correlate signals, map CI + impact set.  
- **Operational State System (OSS)** (optional): system-of-record cho operational state timeline.  
- **Knowledge Base (KB)**: system-of-record cho tri thức + versioning/approval/feedback + search/semantic index.

---

## Goals

- Tạo **kho tri thức có versioning + review/publish workflow** (audit được ai đổi gì, khi nào, vì sao).
- Cho phép **link tri thức với CMDB entities**:
  - `ci_ref=cmdb:<ci_id>`
  - `ci_type_id`, `service`, `team`, `env`, `tags`
  - `incident_id` / `change_request_id` (ITSM)
- Cung cấp **search chuẩn hoá**:
  - keyword + filter/facet
  - “related articles” theo CI + tags + topology neighborhood (optional)
- Cung cấp **API contracts** để:
  - UI/Portal hiển thị tri thức theo CI/Incident/Change
  - EPS/Orchestrator gọi “suggest runbook/RCA” khi có incident candidates
- Hỗ trợ **RAG (optional)**: ingest docs → chunk → embeddings → hybrid retrieval → answer with citations.

---

## Non-goals

- Không thay thế wiki nội bộ nếu tổ chức đã có; KB có thể **federate/import** nhưng vẫn cần system-of-record cho ops knowledge có audit + integration với CMDB.
- Không tự động “điều khiển” production (automation) — KB chỉ cung cấp tri thức và checklist; orchestration thuộc hệ thống khác.
- Không lưu raw logs/metrics; KB chỉ lưu snippets/evidence links cần thiết.

---

## Actors & Use cases

### Actors

- **NOC/SRE/Ops**: tìm runbook khi incident; đề xuất bước xử lý; tạo postmortem/RCA.
- **Change manager / Release manager**: dùng standard change templates + pre/post checks theo impact set.
- **Service owners / App owners**: đóng góp SOP, xác nhận nội dung, ownership.
- **Security/Compliance**: yêu cầu audit + retention + permission phù hợp.

### Use cases (tối thiểu)

1. **CI detail → Knowledge tab**: xem runbook/SOP/RCA liên quan CI.
2. **Incident triage**: từ signal (alert/log/ticket) → map CI → KB suggest runbooks + known issues.
3. **RCA publishing**: sau khi đóng incident, tạo RCA article, link impacted CIs + change evidence.
4. **Change impact**: CR scope → impact set → gợi ý checklist + standard change templates.
5. **Search portal**: tìm theo keyword + filter (team/env/type/tags/CI/service).

---

## Definitions

- **Knowledge Item**: đơn vị tri thức (article/runbook/RCA/template/FAQ).
- **Revision**: phiên bản nội dung (immutable), phục vụ audit + rollback.
- **Evidence**: link hoặc attachment minh chứng (ticket, alert id, log query URL, dashboard snapshot).
- **Chunk**: đoạn nội dung đã chuẩn hoá để index (full-text và/hoặc vector).
- **Hybrid retrieval**: combine BM25 (keyword) + vector similarity (semantic).
- **Citations**: trích dẫn tới revision + chunk ids trong KB.

---

## Architecture Overview

```
Sources (manual authoring / imports / incident closures / EPS artifacts)
        |
        v
KB API (authn/authz, CRUD, workflow, linking to CMDB/ITSM)
        |
        +--> Primary Store (MySQL/PostgreSQL): items, revisions, links, feedback, ACL, audit
        |
        +--> Object Store (S3/MinIO) [optional]: attachments (pdf, images, exports)
        |
        +--> Indexing Pipeline (async worker):
              - extract + normalize
              - chunking
              - full-text index
              - (optional) embeddings + vector index
        |
        +--> Search Engine:
              - OpenSearch/Elastic (BM25 + facets)
              - (optional) vector: OpenSearch kNN / pgvector / Milvus
        |
        +--> UI/Portal + CMDB UI integrations
```

---

## Core Responsibilities

1. **Knowledge system-of-record**:
   - content, metadata, relationships, lifecycle, audit
2. **Workflow**:
   - draft → in_review → published → archived (versioned)
3. **Linking**:
   - KB ↔ `ci_ref` (CMDB), incident IDs, change IDs, services/teams/env
4. **Search**:
   - keyword + facet + ranking (feedback/recency)
5. **Suggestion** (contextual):
   - given `(ci_ref, incident_group_id?, query text?)` return ranked KB items
6. **RAG (optional)**:
   - provide retrieval API returning chunks + citations

---

## Data Model

### Logical entities

#### 1) `kb_items`

- `id` (UUID)
- `type`: `runbook|sop|rca|known_issue|standard_change|faq|doc`
- `status`: `draft|in_review|published|archived`
- `title`
- `summary` (short)
- `owner_team` / `owner_user` (optional)
- `language` (e.g. `vi`, `en`)
- `created_at`, `updated_at`, `published_at`
- `current_revision_id`
- `visibility`: `public|org|team|restricted`

#### 2) `kb_revisions` (immutable content snapshots)

- `id` (UUID)
- `item_id`
- `revision_no` (int)
- `content_format`: `markdown|html|asciidoc|plain`
- `content` (text) hoặc `content_ref` (object store key)
- `change_note` (why changed)
- `created_by`, `created_at`

#### 3) `kb_links` (relationships)

- `id` (UUID)
- `item_id`
- `link_type`: `ci_ref|ci_type|service|incident|change_request|external_url`
- `target_ref`:
  - CI: `cmdb:<ci_id>`
  - CIType: `cmdb_type:<type_id>`
  - Incident: `itsm_incident:<id>` hoặc `eps_group:<group_id>`
  - CR: `itsm_change:<id>`
  - External: URL
- `weight` (optional, manual boost)
- `created_at`, `created_by`

#### 4) `kb_tags`

- `id`, `item_id`, `tag` (string)

#### 5) `kb_feedback`

- `id`, `item_id`, `user_id`
- `rating`: `up|down` (hoặc 1..5)
- `comment` (optional)
- `context_ref` (optional): `cmdb:<ci_id>` / `eps_group:<id>`
- `created_at`

#### 6) `kb_index_jobs` (async indexing state)

- `id`, `revision_id`
- `status`: `pending|running|done|failed`
- `error` (optional)
- `started_at`, `finished_at`

#### 7) `kb_chunks` (for search & citations)

- `id` (UUID)
- `revision_id`
- `chunk_no`
- `text`
- `hash` (dedup)
- `bm25_doc_id` (optional)
- `embedding_vector` (optional) hoặc store in vector index only
- `created_at`

#### 8) `kb_acl` (optional, nếu cần fine-grained)

- `item_id`
- `principal_type`: `user|role|team`
- `principal_id`
- `permission`: `read|write|review|publish|admin`

### Notes

- CMDB permission có thể được dùng như **input** cho KB suggestion (“đừng gợi ý bài mà user không có quyền đọc CI liên quan”), nhưng KB vẫn có ACL riêng.
- `kb_links.target_ref` dùng string namespace để dễ tích hợp nhiều hệ.

---

## Workflows

### 1) Authoring lifecycle

```text
draft -> in_review -> published -> archived
         ^   |             |
         |   +-- request changes
         +-- revert to draft (new revision)
```

Rules (recommend):

- Chỉ `reviewer/publisher` mới publish.
- Publish tạo `published_at` và gắn `current_revision_id`.
- Mọi thay đổi tạo revision mới; không sửa in-place.

### 2) Incident → KB suggestion (triage)

Inputs:

- `ci_ref` (1 hoặc nhiều)
- `incident_group_id` (EPS) hoặc `itsm_incident_id`
- text (title/message)

Outputs:

- top-N KB items (runbook/known_issue) + reason (matched tags/CI/service + similarity) + citations (nếu RAG)

### 3) Post-incident RCA creation

- Khi incident closed, tạo `kb_item` type `rca` (draft) và prefill:
  - impacted CIs (`kb_links`)
  - timeline links (ticket/change refs)
  - evidence refs (dashboards/log queries)
- RCA publish yêu cầu review + redact sensitive info.

### 4) Change impact → checklist/template suggestion

- Input: CR scope CIs + predicted impact set (từ CMDB traversal/EPS)
- Output:
  - `standard_change` templates có links trùng service/team/env/CIType
  - pre/post checklist từ runbooks

---

## Search & Retrieval (BM25 + Vector + RAG)

### 1) Full-text + facet (baseline, must-have)

- Index fields:
  - title, summary, tags, content (chunks), link targets (service/team/env/ci_type)
- Facets:
  - type, status, owner_team, env, service, tags, language, updated_at

Ranking signals (suggest):

- BM25 score (primary)
- Recency boost (recently updated/published)
- Feedback boost (upvotes)
- Link weight boost (manual “pinned” runbooks)

### 2) Semantic search (optional)

Pipeline:

- chunk revision content (e.g. 300–800 tokens)
- embedding model (internal, on-prem preferred)
- store vectors in:
  - OpenSearch kNN, hoặc
  - pgvector (nếu muốn đơn giản), hoặc
  - Milvus (nếu volume lớn)

Retrieval:

- hybrid: combine keyword candidates + vector nearest neighbors
- re-rank by:
  - overlap với `ci_ref` / service / env
  - freshness & feedback

### 3) RAG answer API (optional)

KB không cần “chat” end-to-end; cung cấp retrieval primitives:

- `retrieve(query, context)` → list chunks + citations
- downstream (UI/assistant) có thể generate answer và **phải** kèm citations:
  - `kb_item_id`, `revision_id`, `chunk_id`

Guardrails:

- chỉ dùng published revisions
- redact policy trước khi index
- log prompt + chunk ids (audit)

---

## API & Integration Contracts

### 1) Core KB APIs (internal)

- `POST /api/v1/kb/items` (create draft)
- `GET /api/v1/kb/items/{id}`
- `PATCH /api/v1/kb/items/{id}` (metadata)
- `POST /api/v1/kb/items/{id}/revisions` (new revision content)
- `POST /api/v1/kb/items/{id}/workflow/submit_review`
- `POST /api/v1/kb/items/{id}/workflow/publish`
- `POST /api/v1/kb/items/{id}/workflow/archive`

### 2) Search APIs

- `GET /api/v1/kb/search?q=...&type=...&tag=...&ci_ref=...`
- `GET /api/v1/kb/suggest?ci_ref=cmdb:<id>&q=...&limit=...`

### 3) Retrieval APIs (RAG optional)

- `POST /api/v1/kb/retrieve`
  - body: `{ query, context: { ci_refs, service, env, team }, limit }`
  - return: chunks + citations

### 4) CMDB integration (KB → CMDB, read-only)

Read-only usage (optional nhưng khuyến nghị):

- validate `ci_ref` tồn tại (CI detail)
- lấy metadata (service/team/env/criticality) để auto-tag hoặc constraint permission

### 5) EPS/ITSM integration (events → KB)

- EPS có thể gọi KB suggest khi tạo incident group (triage helper).
- ITSM closure có thể trigger “create RCA draft”.
- Contract idempotent:
  - `source_ref` + `source_event_id` để tránh tạo trùng drafts.

---

## Security, Permissions, Audit

### Authn/Authz

- Authn: reuse SSO/JWT của ecosystem.
- Authz:
  - RBAC: `reader`, `contributor`, `reviewer`, `publisher`, `admin`
  - ABAC (optional): based on `team/env/tenant` tags + CI visibility

### Visibility rules (recommend)

- Item có `visibility` độc lập, nhưng **không được leak CI-sensitive**:
  - nếu item link đến CI mà user không có quyền read, policy options:
    1) hide item entirely (simple)
    2) show item nhưng redact CI links (khó audit; không khuyến nghị)

### Audit

- Log mọi workflow action (submit/review/publish/archive) + actor + time.
- Immutable revisions giúp audit/rollback.
- RAG/retrieval phải log: `user_id`, `query`, `returned_chunk_ids` (không log secrets).

---

## Reliability, Idempotency, Retention

- Indexing là async; API trả status:
  - published revision chưa index xong vẫn có thể xem trực tiếp (read path from primary store)
- Idempotency:
  - import/auto-create drafts dùng `(source_ref, source_id)` unique key
- Retention:
  - revisions giữ lâu (audit), nhưng có policy:
    - archive + freeze (no further edits)
    - purge attachments theo compliance
- Backpressure:
  - queue cho indexing jobs; retry with DLQ; rate limit embedding.

---

## Observability

- Metrics:
  - search QPS, p50/p95 latency
  - index job lag + failures
  - suggestion usage + click-through
  - feedback ratio (up/down)
- Logs:
  - structured: `request_id`, `item_id`, `revision_id`, `user_id`
- Tracing:
  - search request → filter → retrieval → CMDB metadata lookup (optional)

---

## Deployment Options

### Option A — KB as a separate service (recommended)

- Pros: boundary rõ, scaling index/search riêng, không làm nặng CMDB core.
- Cons: thêm service vận hành.

Suggested stack (align repo ecosystem):

- API: Python/Flask (giống cmdb-api) hoặc Go
- DB: MySQL/PostgreSQL
- Cache/queue: Redis + worker (Celery/RQ/Asynq)
- Search: OpenSearch/Elastic (BM25 + facets)
- Vector: OpenSearch kNN / pgvector / Milvus (optional)
- Object store: MinIO/S3 (optional)

### Option B — KB module inside CMDB API

- Pros: reuse auth/ACL, deploy đơn giản.
- Cons: coupling; indexing/embedding workloads có thể ảnh hưởng CMDB latency.

Khuyến nghị nếu chọn B: tách worker/process và giới hạn resources, dùng outbox/queue.

---

## Phased Rollout

1. **Phase 0 (must-have)**: KB CRUD + versioning + publish workflow + keyword search + CI linking (no embeddings).
2. **Phase 1**: Suggestion theo CI/service/team + feedback ranking.
3. **Phase 2**: Auto-create RCA draft từ incident closure + templates cho standard change.
4. **Phase 3 (optional)**: semantic search + hybrid retrieval + citations API (RAG-ready).

---

## Open Questions

1. Nguồn ITSM cụ thể (ServiceNow/Jira/…) và field mapping cho `incident_id`/`change_request_id`?
2. Có yêu cầu multi-tenant/org isolation không? (ảnh hưởng ACL + index partitioning)
3. “Service/team/env/criticality” hiện có trong CMDB attributes chưa (để auto-tag + permission)?
4. Volume docs/attachments dự kiến? (quyết định OpenSearch vs pgvector vs Milvus)
5. Chính sách compliance: retention, PII redaction, ai được publish runbooks?


