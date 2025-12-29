# Technical Design Document (TDD)
## CMDB System - Configuration Management Database

**Version:** 1.0  
**Date:** 2025-12-04  
**Author:** CMDB Development Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Frontend Architecture (cmdb-ui)](#frontend-architecture-cmdb-ui)
5. [Request Flow (UI to API)](#request-flow-ui-to-api)
6. [Core Components](#core-components)
7. [Data Model](#data-model)
8. [API Design](#api-design)
9. [Auto-Discovery System](#auto-discovery-system)
10. [IPAM Module](#ipam-module)
11. [Security & Permissions](#security--permissions)
12. [Caching Strategy](#caching-strategy)
13. [Elasticsearch Configuration](#elasticsearch-configuration)
14. [Deployment Architecture](#deployment-architecture)
15. [Performance Considerations](#performance-considerations)
16. [Future Enhancements](#future-enhancements)

---

## Executive Summary

CMDB (Configuration Management Database) is a flexible, lightweight, and highly customizable configuration management system designed for IT operations teams. The system provides comprehensive asset management, automatic resource discovery, IP address management (IPAM), and data center infrastructure management (DCIM) capabilities.

### Key Features
- **Flexible Model Configuration**: Custom CI types, attributes, and relationships
- **Auto-Discovery**: Support for SNMP, HTTP/API-based discovery, and plugin scripts
- **IPAM**: Complete IP address and subnet management
- **DCIM**: Data center infrastructure management
- **Fine-grained Permissions**: Role-based access control (RBAC)
- **Multi-dimensional Views**: Resource, hierarchical, and relationship views

---

## System Overview

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python 3.8-3.11, Flask 2.2.5, Flask-RESTful |
| Frontend UI | Vue.js, Ant Design Vue |
| Database | MySQL 5.7+, SQLAlchemy ORM |
| Cache | Redis 4.6.0+ |
| Search | Elasticsearch 7.17.9 (optional) |
| Task Queue | Celery 5.3.1 |

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      CMDB System                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │   Web UI     │    │   REST API   │                      │
│  │  (Vue.js)    │◄───┤  (Flask)     │                      │
│  └──────────────┘    └──────┬───────┘                      │
│                              │                             │
│  ┌───────────────────────────┼───────────────────────────┐ │
│  │                          │                           │ │
│  │  ┌──────────┐  ┌─────────▼────────┐  ┌──────────┐   │ │
│  │  │  MySQL   │  │     Redis        │  │  Celery  │   │ │
│  │  │ Database │  │     Cache        │  │  Workers │   │ │
│  │  └──────────┘  └──────────────────┘  └──────────┘   │ │
│  │                                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │ │
│  │  │Elastic-  │  │  SNMP    │  │  Cloud   │      │ │
│  │  │search    │  │  Devices │  │  APIs    │      │ │
│  │  └──────────┘  └──────────┘  └──────────┘      │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

### 3-Tier Architecture

1. **Presentation Layer**: Vue.js frontend with Ant Design Vue components
2. **Application Layer**: Flask REST API with business logic
3. **Data Layer**: MySQL for persistent storage, Redis for caching

### Request Flow

```
User Request
    │
    ▼
┌─────────────────┐
│   Vue.js UI     │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask API      │
│  - Auth         │
│  - Validation   │
│  - Business     │
│    Logic        │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ MySQL  │ │ Redis  │
│        │ │ Cache  │
└────────┘ └────────┘
```

### Module Structure

```
cmdb-api/
├── api/
│   ├── app.py                 # Flask application factory
│   ├── extensions.py          # Flask extensions (db, cache, etc.)
│   ├── lib/
│   │   └── cmdb/
│   │       ├── ci.py          # CI management
│   │       ├── ci_type.py     # CI type management
│   │       ├── attribute.py   # Attribute management
│   │       ├── auto_discovery/ # Auto-discovery engine
│   │       ├── ipam/          # IPAM module
│   │       ├── dcim/          # DCIM module
│   │       ├── search/        # Search engine
│   │       └── perms.py       # Permission management
│   ├── models/
│   │   └── cmdb.py            # SQLAlchemy models
│   ├── views/
│   │   └── cmdb/              # REST API endpoints
│   └── tasks/
│       └── cmdb.py            # Celery background tasks
└── tests/                     # Unit and integration tests
```

---

## Frontend Architecture (cmdb-ui)

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | Vue.js 2.x |
| UI Library | Ant Design Vue |
| HTTP Client | Axios |
| State Management | Vuex |
| Router | Vue Router |
| Build Tool | Webpack |
| Language | JavaScript (ES6+) |

### Project Structure

```
cmdb-ui/src/
├── api/                    # API client functions
│   ├── cmdb.js            # CMDB API calls
│   ├── auth.js            # Authentication API
│   └── index.js           # API endpoint definitions
├── modules/               # Feature modules
│   └── cmdb/              # CMDB module
│       ├── api/           # Module-specific API calls
│       │   ├── ci.js      # CI API
│       │   ├── CIType.js  # CI Type API
│       │   ├── ipam.js    # IPAM API
│       │   └── discovery.js # Discovery API
│       ├── components/     # Reusable components
│       │   ├── ciTable/   # CI table component
│       │   ├── cmdbGrant/ # Permission grant component
│       │   └── searchForm/ # Search form component
│       ├── views/         # Page views
│       │   ├── ci/        # CI management pages
│       │   ├── ci_types/  # CI type configuration
│       │   ├── ipam/      # IPAM pages
│       │   ├── discovery/ # Discovery pages
│       │   └── dcim/      # DCIM pages
│       ├── router/        # Module routes
│       └── store/         # Module state
├── components/            # Global components
├── layouts/              # Layout components
│   ├── BasicLayout.vue   # Main layout
│   └── UserLayout.vue    # Login layout
├── router/               # Global router
├── store/                # Global state
├── utils/                # Utility functions
│   ├── request.js        # Axios interceptor
│   └── axios.js          # Axios setup
└── main.js               # Application entry
```

### Key Components

#### 1. API Client Layer (`src/utils/request.js`)

**Axios Configuration**:
```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL,
  timeout: 6000,
  withCredentials: true,
  crossDomain: true
})
```

**Request Interceptor**:
- Adds `Access-Token` header from localStorage
- Adds `Accept-Language` header for i18n
- Handles authentication tokens

**Response Interceptor**:
- Returns `response.data` directly
- Error handling with user-friendly messages
- 401 redirect to login
- 412 handling for concurrent requests

#### 2. Module API Layer (`src/modules/cmdb/api/`)

**CI API** (`ci.js`):
```javascript
export function searchCI(params, isShowMessage = true)
export function addCI(params)
export function updateCI(id, params, isShowMessage = true)
export function deleteCI(ciId, isShowMessage = true)
export function getCIById(ciId)
```

**IPAM API** (`ipam.js`):
```javascript
export function getIPAMSubnet()
export function postIPAMSubnet(data)
export function getIPAMAddress(params)
export function getIPAMStats(params)
```

**Discovery API** (`discovery.js`):
- Rule management
- Discovered CI queue
- Accept/reject operations

#### 3. View Components

**CI Management** (`views/ci/`):
- `index.vue`: CI list and search
- `ciDetailPage.vue`: CI detail view
- `modules/`: Sub-components (attributes, relations, history)

**CI Type Configuration** (`views/ci_types/`):
- `index.vue`: CI type list
- `ciTypedetail.vue`: CI type detail
- `attributeEditForm.vue`: Attribute editor
- `relationAD.vue`: Auto-discovery relationship config
- `triggerForm.vue`: Trigger configuration

**IPAM** (`views/ipam/`):
- Subnet tree view
- IP address table
- Statistics dashboard
- History views

**Discovery** (`views/discovery/`):
- Rule management
- Discovered CI queue
- Account configuration

#### 4. Reusable Components

**ciTable** (`components/ciTable/`):
- Data table for CIs
- Sorting, filtering, pagination
- Bulk operations

**cmdbGrant** (`components/cmdbGrant/`):
- Permission grant modal
- Role selection
- Permission checkbox groups

**searchForm** (`components/searchForm/`):
- Advanced search form
- Query builder
- Filter management

### State Management

**Vuex Store Structure**:
```
store/
├── global/          # Global state
│   ├── user.js     # User info
│   └── app.js      # App config
└── modules/
    └── cmdb/       # CMDB module state
```

**State Properties**:
- User information
- CI type cache
- Permission cache
- UI preferences

### Routing

**Dynamic Route Generation**:
```javascript
// From router/config.js
export const generatorDynamicRouter = async () => {
  const packages = []
  const { apps = undefined } = store.getters.userInfo
  
  for (const appName of appConfig.buildModules) {
    if (!apps || apps.includes(appName)) {
      const module = await import(`@/modules/${appName}/index.js`)
      const r = await module.default.route()
      packages.push(...r)
    }
  }
  return packages
}
```

**Route Guards** (`guard.js`):
- Authentication check
- Permission validation
- Redirect to login if unauthorized

---

## Request Flow (UI to API)

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────┐
│                    User Action                          │
│  (Click button, submit form, navigate page)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Vue Component                              │
│  (views/ci/index.vue, views/ipam/...)                  │
│  - User interaction handler                             │
│  - Form validation                                      │
│  - Data preparation                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           API Client Function                           │
│  (modules/cmdb/api/ci.js, ipam.js, ...)                 │
│  - Function call: searchCI(params)                      │
│  - Parameter formatting                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Axios Request Interceptor                       │
│  (utils/request.js)                                      │
│  - Add Access-Token header                              │
│  - Add Accept-Language header                           │
│  - Add withCredentials                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Request
                     │ GET /api/v0.1/ci/s?q=_type:server
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask API Server                           │
│  (cmdb-api/api/views/cmdb/ci.py)                        │
│  - Request validation                                   │
│  - Permission check                                     │
│  - Business logic                                       │
│  - Database query                                       │
│  - Response formatting                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Response
                     │ { code: 200, result: [...], ... }
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        Axios Response Interceptor                        │
│  (utils/request.js)                                      │
│  - Extract response.data                                │
│  - Error handling                                       │
│  - Show error messages                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           API Client Function                           │
│  - Return data to component                             │
│  - Promise resolution                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Vue Component                              │
│  - Update component data                                │
│  - Re-render UI                                         │
│  - Show loading/error states                            │
└─────────────────────────────────────────────────────────┘
```

### Example: CI Search Flow

**1. User Action**:
```javascript
// User types in search box and clicks "Search"
// Component: views/ci/index.vue
```

**2. Component Handler**:
```javascript
// views/ci/index.vue
async handleSearch() {
  this.loading = true
  try {
    const params = {
      q: this.searchQuery,
      page: this.currentPage,
      count: this.pageSize
    }
    const res = await searchCI(params)
    this.ciList = res.result
    this.total = res.numfound
  } catch (error) {
    this.$message.error('Search failed')
  } finally {
    this.loading = false
  }
}
```

**3. API Call**:
```javascript
// modules/cmdb/api/ci.js
export function searchCI(params, isShowMessage = true) {
  return axios({
    url: '/v0.1/ci/s',
    method: 'GET',
    params: params,
    isShowMessage
  })
}
```

**4. Request Interceptor**:
```javascript
// utils/request.js
service.interceptors.request.use(config => {
  const token = Vue.ls.get(ACCESS_TOKEN)
  if (token) {
    config.headers['Access-Token'] = token
  }
  config.headers['Accept-Language'] = store?.state?.locale ?? 'zh'
  return config
})
```

**5. API Server Processing**:
```python
# api/views/cmdb/ci.py
class CISearchView(APIView):
    def get(self):
        query = request.values.get('q', "")
        s = ci_search(query, fl, facet, page, ret_key, count, sort)
        response, counter, total, page, numfound, facet = s.search()
        return self.jsonify(
            numfound=numfound,
            total=total,
            page=page,
            result=response
        )
```

**6. Response Handling**:
```javascript
// utils/request.js
service.interceptors.response.use((response) => {
  return response.data  // Extract data from response
}, err)  // Error handler shows message
```

**7. Component Update**:
```javascript
// Component receives data and updates UI
this.ciList = res.result  // Update table data
this.total = res.numfound  // Update pagination
```

### Error Handling Flow

```
API Error Response
    │
    ▼
Response Interceptor (utils/request.js)
    │
    ├── 401 Unauthorized
    │   └── Redirect to /user/login
    │
    ├── 412 Precondition Failed
    │   └── Show wait notification
    │
    ├── 5xx Server Error
    │   └── Show error message
    │
    └── Other Errors
        └── Show error message from response
```

### Authentication Flow

```
User Login
    │
    ▼
POST /api/v1/acl/login
    │
    ├── Success
    │   ├── Store token in localStorage
    │   ├── Store user info in Vuex
    │   └── Redirect to dashboard
    │
    └── Failure
        └── Show error message

Subsequent Requests
    │
    ▼
Request Interceptor adds Access-Token header
    │
    ▼
API validates token
    │
    ├── Valid
    │   └── Process request
    │
    └── Invalid/Expired
        └── 401 Response → Redirect to login
```

### Permission Check Flow

```
Component Mount
    │
    ▼
Check User Permissions (Vuex store)
    │
    ├── Has Permission
    │   └── Render component
    │
    └── No Permission
        └── Show "No Permission" page

API Request
    │
    ▼
API Server Permission Check
    │
    ├── Has Permission
    │   └── Return data
    │
    └── No Permission
        └── 403 Forbidden → Show error
```

---

## Core Components

### 1. CI (Configuration Item) Management

**Purpose**: Core entity representing any IT resource (server, network device, application, etc.)

**Key Classes**:
- `CIManager`: CRUD operations for CIs
- `CIRelationManager`: Relationship management between CIs

**Features**:
- Create, read, update, delete CIs
- Support for custom attributes
- Status management (REVIEW, VALIDATE)
- Soft delete mechanism
- History tracking

### 2. CI Type Management

**Purpose**: Define templates/schemas for different types of CIs

**Key Classes**:
- `CITypeManager`: Manage CI type definitions
- `CITypeAttributeManager`: Manage attributes for CI types

**Features**:
- Custom CI type creation
- Attribute definition (text, int, float, datetime, reference, etc.)
- Unique constraints
- Computed attributes
- Attribute groups
- Inheritance support

### 3. Relationship Management

**Purpose**: Define and manage relationships between CIs

**Key Classes**:
- `CIRelationManager`: Manage CI relationships
- `RelationTypeManager`: Manage relationship types

**Features**:
- One-to-One, One-to-Many, Many-to-Many relationships
- Relationship constraints
- Relationship views
- Topology visualization

### 4. Search Engine

**Purpose**: Fast and flexible search across CIs

**Components**:
- `SearchFromDB`: Database-based search
- `SearchFromES`: Elasticsearch-based search (optional)

**Features**:
- Query language: `_type:server AND status:VALIDATE`
- Field filtering
- Pagination
- Sorting
- Permission-aware search

### 5. Auto-Discovery System

**Purpose**: Automatically discover and ingest IT resources

**Components**:
- `AutoDiscoveryCITypeCRUD`: Discovery rule management
- `AutoDiscoveryRule`: Discovery rule definitions
- `AutoDiscoveryCI`: Discovered CI queue
- `AutoDiscoveryCITypeRelation`: Relationship configuration for discovered CIs

**Discovery Types**:
- **Plugin**: SQL/Python script-based discovery
- **SNMP**: Network device discovery via SNMP
- **HTTP**: Cloud resource discovery via REST APIs

**Server-Side Flow**:
```
Data Ingestion API
    │
    ▼
┌─────────────────┐
│  Discovered CI  │
│     Queue       │
│  (ad_cis table) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Accept/Reject  │
│     Process     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CI Created     │
│  (via CIManager)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Relationships  │
│  Built (async)  │
└─────────────────┘
```

### 6. IPAM Module

**Purpose**: IP Address and Subnet Management

**Components**:
- `SubnetManager`: Subnet CRUD and tree view
- `IpAddressManager`: IP address assignment
- `Stats`: IPAM statistics

**Features**:
- Subnet tree hierarchy
- IP address assignment (ASSIGN, USED, FREE)
- Auto-assignment from discovery
- Subnet scanning
- Statistics (total, assigned, used, free)

**Data Flow**:
```
Subnet (CIDR: 10.0.0.0/24)
    │
    ├── Subnet (10.0.0.0/26)
    │   ├── IP: 10.0.0.1 (ASSIGNED)
    │   ├── IP: 10.0.0.2 (USED)
    │   └── IP: 10.0.0.3-62 (FREE)
    │
    └── Subnet (10.0.0.64/26)
        └── ...
```

### 7. DCIM Module

**Purpose**: Data Center Infrastructure Management

**Components**:
- `IDCManager`: Data center management
- `ServerRoomManager`: Server room management
- `RackManager`: Rack management
- `RegionManager`: Region management

**Features**:
- Hierarchical structure: Region → IDC → Server Room → Rack
- Tree view visualization
- Asset tracking

---

## Data Model

### Core Tables

#### `c_ci_types`
CI type definitions

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR(32) | CI type name |
| alias | VARCHAR(32) | Display alias |
| unique_id | INT | Unique attribute ID |
| show_id | INT | Display attribute ID |
| enabled | BOOLEAN | Enabled status |
| icon | TEXT | Icon data |

#### `c_attributes`
Attribute definitions

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR(32) | Attribute name |
| alias | VARCHAR(32) | Display alias |
| value_type | ENUM | Value type (TEXT, INT, FLOAT, etc.) |
| is_choice | BOOLEAN | Is choice list |
| choice_value | JSON | Choice values |

#### `c_ci_type_attributes`
CI type attribute mappings

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| type_id | INT | CI type ID |
| attr_id | INT | Attribute ID |
| is_required | BOOLEAN | Required flag |
| is_readonly | BOOLEAN | Readonly flag |
| default_value | TEXT | Default value |

#### `c_cis`
Configuration Items

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| type_id | INT | CI type ID |
| status | ENUM | Status (REVIEW, VALIDATE) |
| deleted | BOOLEAN | Soft delete flag |
| created_at | DATETIME | Creation time |
| updated_at | DATETIME | Update time |

#### `c_ci_attributes`
CI attribute values (EAV pattern)

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| ci_id | INT | CI ID |
| attr_id | INT | Attribute ID |
| value | TEXT | Attribute value |

#### `c_ci_relations`
CI relationships

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| first_ci_id | INT | Source CI ID |
| second_ci_id | INT | Target CI ID |
| relation_type_id | INT | Relation type ID |
| deleted | BOOLEAN | Soft delete flag |

### Auto-Discovery Tables

#### `ad_rules`
Auto-discovery rules

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR(64) | Rule name |
| ci_type_name | VARCHAR(32) | Target CI type |
| discovery_type | ENUM | Type (plugin, snmp, http) |
| plugin_script | TEXT | Plugin script |
| enabled | BOOLEAN | Enabled status |

#### `ad_cis`
Discovered CIs queue

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| rule_id | INT | Rule ID |
| ci_type_name | VARCHAR(32) | CI type |
| data | JSON | Discovered data |
| status | ENUM | Status (QUEUED, ACCEPTED, REJECTED) |

### IPAM Tables

#### `ipam_subnet_scans`
Subnet scan configurations

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| ci_id | INT | Subnet CI ID |
| agent_id | VARCHAR(64) | External discovery agent identifier (optional) |
| scan_enabled | BOOLEAN | Scan enabled |

---

## API Design

### API Versioning
- Base URL: `/api/v0.1`
- ACL API: `/api/v1/acl`
- Common Setting API: `/api/common-setting/v1`

### Authentication
- Session-based (Flask-Login)
- API Key authentication
- OAuth2 support

### Common Response Format

```json
{
  "code": 200,
  "message": "success",
  "result": {...},
  "numfound": 100,
  "page": 1,
  "page_size": 20
}
```

### Key Endpoints

#### CI Management
- `GET /api/v0.1/ci/s` - Search CIs
- `GET /api/v0.1/ci/<int:ci_id>` - Get CI details
- `POST /api/v0.1/ci` - Create CI
- `PUT /api/v0.1/ci/<int:ci_id>` - Update CI
- `DELETE /api/v0.1/ci/<int:ci_id>` - Delete CI

#### CI Type Management
- `GET /api/v0.1/ci_types` - List CI types
- `POST /api/v0.1/ci_types` - Create CI type
- `PUT /api/v0.1/ci_types/<int:type_id>` - Update CI type
- `DELETE /api/v0.1/ci_types/<int:type_id>` - Delete CI type

#### Auto-Discovery
- `GET /api/v0.1/adr` - List discovery rules
- `POST /api/v0.1/adr` - Create discovery rule
- `GET /api/v0.1/ad/ci` - List discovered CIs
- `POST /api/v0.1/ad/accept` - Accept discovered CI
- `POST /api/v0.1/ad/reject` - Reject discovered CI

#### IPAM
- `GET /api/v0.1/ipam/subnet` - Get subnet tree
- `POST /api/v0.1/ipam/subnet` - Create subnet
- `GET /api/v0.1/ipam/subnet/<int:subnet_id>/address` - Get IP addresses
- `POST /api/v0.1/ipam/subnet/<int:subnet_id>/address/assign` - Assign IP
- `GET /api/v0.1/ipam/stats` - Get IPAM statistics

---

## Auto-Discovery System

### Module Overview

**Location**: `api/lib/cmdb/auto_discovery/auto_discovery.py`

**Main Classes**:
- `AutoDiscoveryRuleCRUD`: Discovery rule management
- `AutoDiscoveryCITypeCRUD`: CI type discovery configuration
- `AutoDiscoveryCICRUD`: Discovered CI queue management
- `AutoDiscoveryCITypeRelationCRUD`: Relationship configuration for discovered CIs
- `AutoDiscoveryHTTPManager`: Cloud provider integration
- `AutoDiscoverySNMPManager`: SNMP discovery support

### Architecture (Server-Side)

```
┌─────────────────────────────────────────────────────────┐
│              CMDB Auto-Discovery Module                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AutoDiscoveryCITypeCRUD                          │  │
│  │  - Rule Management (CRUD)                        │  │
│  │  - Rule Sync API (get method)                     │  │
│  │  - Attribute Mapping                               │  │
│  └───────────────┬────────────────────────────────────┘  │
│                  │                                       │
│  ┌───────────────▼──────────────────────────────────┐  │
│  │  AutoDiscoveryCICRUD                             │  │
│  │  - Discovered CI Queue Management                │  │
│  │  - Accept/Reject Logic                           │  │
│  │  - IP Auto-Assignment                             │  │
│  │  - Data Transformation                            │  │
│  └───────────────┬──────────────────────────────────┘  │
│                  │                                       │
│  ┌───────────────▼──────────────────────────────────┐  │
│  │  AutoDiscoveryCITypeRelationCRUD                 │  │
│  │  - Relationship Configuration                     │  │
│  │  - is_reverse Flag Management                     │  │
│  └───────────────┬──────────────────────────────────┘  │
│                  │                                       │
│  ┌───────────────▼──────────────────────────────────┐  │
│  │  build_relations_for_ad_accept (Celery Task)    │  │
│  │  - Async Relationship Building                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Endpoints                                    │  │
│  │  - POST /api/v0.1/ad/ingest (data ingestion)     │  │
│  │  - GET /api/v0.1/ad/rule (rule sync)            │  │
│  │  - POST /api/v0.1/ad/accept (accept CI)          │  │
│  │  - POST /api/v0.1/ad/reject (reject CI)          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Discovery Process (Server-Side Flow)

**1. Rule Definition** (`AutoDiscoveryCITypeCRUD`)
- Admin creates discovery rules via UI or API
- Rule contains:
  - `adr_id`: Reference to `AutoDiscoveryRule` (plugin script)
  - `type_id`: Target CI type
  - `agent_id`: Specific agent (optional)
  - `query_expr`: Query expression to match CIs (optional)
  - `attributes`: Mapping from discovery keys to CI attributes
  - `extra_option`: Additional configuration (credentials, etc.)

**2. Rule Sync API** (`AutoDiscoveryCITypeCRUD.get()`)
```python
# From auto_discovery.py:250-320
def get(cls, ci_id, oneagent_id, oneagent_name, last_update_at=None):
    """
    API endpoint for rule synchronization
    Returns discovery rules applicable to the requesting client
    Supports incremental sync via last_update_at parameter
    """
    rules = cls.cls.get_by(to_dict=True)
    
    for rule in rules:
        if not rule['enabled']:
            continue
        
        # Rule matching logic:
        # 1. Direct agent_id match
        if oneagent_id and rule['agent_id'] == oneagent_id:
            result.append(rule)
        
        # 2. Query expression match (CI must match query)
        elif rule['query_expr']:
            query = rule['query_expr'].lstrip('q').lstrip('=')
            s = ci_search(query, fl=['_id'], count=1000000)
            response, _, _, _, _, _ = s.search()
            for i in (response or []):
                if i.get('_id') == ci_id:
                    result.append(rule)
                    break
        
        # 3. Default rules (no agent_id, no query_expr)
        elif not rule['agent_id'] and not rule['query_expr']:
            result.append(rule)
    
    # Return rules with last_update_at for incremental sync
    return result, new_last_update_at
```

**3. Data Ingestion API** (`/api/v0.1/ad/ingest`)
- Receives discovered CI data via REST API
- Validates and stores data in `ad_cis` table with status `QUEUED`
- Signature verification for security
- Supports batch ingestion

**4. Discovered CI Queue Management**
- CIs stored in `ad_cis` table with status tracking
- Status values: `QUEUED`, `ACCEPTED`, `REJECTED`
- Queue can be filtered and searched via API

**5. Accept Process** (`AutoDiscoveryCICRUD.accept()`)
```python
# From auto_discovery.py:708-869
def accept(cls, adc, adc_id=None, nickname=None):
    """
    Accept discovered CI and create actual CI
    """
    # 1. Get discovery rule configuration
    adt = AutoDiscoveryCITypeCRUD.get_by_id(adc.adt_id)
    ad_key2attr = adt.attributes or {}
    
    # 2. Map discovery keys to CI attributes
    ci_dict = {ad_key2attr[k]: v 
               for k, v in adc.instance.items() 
               if k in ad_key2attr}
    
    # 3. Apply value mappings (for cloud providers)
    mapping, path_mapping = AutoDiscoveryHTTPManager.get_predefined_value_mapping(...)
    if mapping:
        ci_dict = {k: (mapping.get(k) or {}).get(str(v), v) 
                   for k, v in ci_dict.items()}
    
    # 4. Create CI
    ci_id = CIManager.add(adc.type_id, is_auto_discovery=True, 
                          _is_admin=True, **ci_dict)
    
    # 5. Build relationships (async)
    build_relations_for_ad_accept.apply_async(
        args=(adc.to_dict(), ci_id, ad_key2attr), 
        queue=CMDB_QUEUE
    )
    
    # 6. Auto-assign IP if applicable
    if ci_type.name == BuiltinModelEnum.IPAM_ADDRESS:
        # IP auto-assignment logic (see below)
        ...
    
    # 7. Mark as accepted
    adc.update(is_accept=True, accept_by=nickname, 
               accept_time=datetime.datetime.now(), ci_id=ci_id)
```

**6. Relationship Building** (`build_relations_for_ad_accept`)
```python
# From tasks/cmdb.py
@celery.task
def build_relations_for_ad_accept(adc_dict, ci_id, ad_key2attr):
    """
    Build relationships based on AutoDiscoveryCITypeRelation rules
    """
    ad_type_id = adc_dict['adt_id']
    relations = AutoDiscoveryCITypeRelation.get_by(ad_type_id=ad_type_id)
    
    for rel in relations:
        # Get peer CI ID from discovery data
        peer_ci_id = adc_dict['instance'].get(rel.ad_key)
        
        if peer_ci_id:
            # Determine relationship direction
            if rel.is_reverse:
                first_ci_id = peer_ci_id
                second_ci_id = ci_id
            else:
                first_ci_id = ci_id
                second_ci_id = peer_ci_id
            
            # Create relationship
            CIRelationManager.add(first_ci_id, second_ci_id, 
                                 rel.relation_type_id)
```

**7. IP Auto-Assignment** (Detailed)
```python
# From auto_discovery.py:740-859
if ci_type.name == BuiltinModelEnum.IPAM_ADDRESS:
    ip = ci_dict.get(IPAddressBuiltinAttributes.IP)
    subnet_id = ci_dict.get('subnet_id')
    cidr = ci_dict.get('cidr')
    ip_network_segment_vlan = ci_dict.get('ip_network_segment_vlan')
    
    # Priority 1: Use subnet_id if provided
    if subnet_id and not cidr:
        subnet = CIManager.get_ci_by_id(subnet_id)
        cidr = subnet.get(SubnetBuiltinAttributes.CIDR)
    
    # Priority 2: Match ip_network_segment_vlan with subnet CIDR
    if ip_network_segment_vlan and not subnet_id and not cidr:
        # Search for subnet with CIDR matching ip_network_segment_vlan
        query = "_type:{},{}:{}".format(
            subnet_type.id,
            cidr_attr.id,
            ip_network_segment_vlan
        )
        response, _, _, _, _, _ = ci_search(query, count=1).search()
        if response:
            subnet_id = response[0]['_id']
            cidr = response[0].get(SubnetBuiltinAttributes.CIDR)
    
    # Priority 3: Use cidr directly
    if subnet_id or cidr:
        IpAddressManager().assign_ips(
            [ip],
            subnet_id,
            cidr,
            assign_status=IPAddressAssignStatus.ASSIGNED,
            **assign_kwargs
        )
```

### Discovery Rule Types (Server Configuration)

**AutoDiscoveryRule** model supports:
- `type`: Discovery type enum (`plugin`, `snmp`, `http`)
- `name`: Rule name
- `plugin_script`: SQL/Python script content (for plugin type)
- `attributes`: Attribute mapping configuration
- `enabled`: Enable/disable flag

**AutoDiscoveryCIType** configuration:
- `adr_id`: Reference to `AutoDiscoveryRule`
- `type_id`: Target CI type ID
- `agent_id`: Optional agent identifier filter
- `query_expr`: Optional query expression to match CIs
- `attributes`: Mapping from discovery keys to CI attributes
- `extra_option`: Additional configuration (credentials, provider settings)

**Supported Discovery Types**:
1. **Plugin**: SQL/Python script-based discovery
2. **SNMP**: Network device discovery via SNMP
3. **HTTP**: Cloud provider API discovery (AWS, Aliyun, Tencent, Huawei)

### Relationship Configuration

**AutoDiscoveryCITypeRelation**:
- `ad_key`: Key in discovery data to find peer CI
- `peer_type_id`: Type of peer CI
- `peer_attr_id`: Attribute to match peer CI
- `relation_type_id`: Type of relationship
- **`is_reverse`**: Boolean flag to reverse direction
  - `false`: `ci_id` → `peer_ci_id` (normal)
  - `true`: `peer_ci_id` → `ci_id` (reversed)

### Auto-Accept Logic

When `auto_accept=True`:
1. Discovered CI is automatically accepted
2. IP addresses are auto-assigned if applicable
3. Relationships are built automatically (async)
4. Network device ports are added (if applicable)

### Performance Optimizations

1. **Incremental Rule Sync**: Only sync changed rules using `last_update_at` timestamp
2. **Batch Processing**: Process multiple discovered CIs in batches
3. **Async Relationship Building**: Use Celery for background processing
4. **Query Optimization**: Efficient CI search for rule matching
5. **Cache Rule Configurations**: Cache discovery rule mappings in Redis
6. **Async IP Assignment**: IP auto-assignment doesn't block accept process

---

## Detailed Processing Flows

### CI Management Flow

#### Create CI Flow

```
User fills form in UI
    │
    ▼
Component validates form data
    │
    ▼
POST /api/v0.1/ci
    │
    ▼
API: CIManager.add()
    │
    ├── Validate attributes
    ├── Check unique constraints
    ├── Check permissions
    ├── Insert into c_cis
    ├── Insert into c_ci_attributes (EAV)
    ├── Update Redis cache
    └── Trigger Celery task (ci_cache)
        │
        ├── Update Elasticsearch (if enabled)
        ├── Build relationships
        └── Fire triggers
    │
    ▼
Return CI ID to UI
    │
    ▼
UI shows success message
UI redirects to CI detail page
```

#### Update CI Flow

```
User edits CI in UI
    │
    ▼
Component loads current CI data
    │
    ▼
PUT /api/v0.1/ci/{ci_id}
    │
    ▼
API: CIManager.update()
    │
    ├── Validate changes
    ├── Check permissions
    ├── Update c_cis table
    ├── Update c_ci_attributes (EAV)
    ├── Record history
    ├── Update Redis cache
    └── Trigger Celery task (ci_cache)
    │
    ▼
Return updated CI data
    │
    ▼
UI refreshes CI detail view
```

#### Search CI Flow

```
User enters search query
    │
    ▼
GET /api/v0.1/ci/s?q=_type:server&page=1
    │
    ▼
API: CISearchView.get()
    │
    ├── Parse query string
    ├── Check permissions (CIFilterPermsCRUD)
    ├── SearchFromDB.search()
    │   ├── Build SQL query
    │   ├── Apply type filters
    │   ├── Apply attribute filters
    │   ├── Apply permission filters
    │   └── Execute query with pagination
    │
    └── Return results
    │
    ▼
UI displays results in table
```

### IPAM Flow

#### Subnet Tree View Flow

```
User opens IPAM page
    │
    ▼
GET /api/v0.1/ipam/subnet
    │
    ▼
API: SubnetView.get()
    │
    ├── SubnetManager.tree_view()
    │   ├── SearchFromDB("_type:IPAM_SUBNET")
    │   ├── Get all subnets
    │   ├── Get relationships (CIRelation)
    │   ├── Build tree structure
    │   └── Sort by _id
    │
    └── Return tree data
    │
    ▼
UI renders tree component
User clicks subnet node
    │
    ▼
GET /api/v0.1/ipam/subnet/{id}/address?cidr=10.0.0.0/24
    │
    ▼
API: AddressView.get()
    │
    ├── Validate subnet
    ├── Get IP addresses from subnet
    ├── Calculate statistics
    └── Return address list
    │
    ▼
UI displays IP address table
```

#### IP Assignment Flow

```
User selects IPs and clicks "Assign"
    │
    ▼
POST /api/v0.1/ipam/subnet/{id}/address/assign
    │
    Body: { ips: ["10.0.0.1", "10.0.0.2"], ... }
    │
    ▼
API: AddressView.post()
    │
    ├── IpAddressManager.assign_ips()
    │   ├── Validate IPs in subnet range
    │   ├── Check if IPs already assigned
    │   ├── Insert into c_ci_attributes
    │   ├── Update subnet counters
    │   │   ├── assign_count
    │   │   ├── used_count
    │   │   └── free_count
    │   └── Record history
    │
    └── Return success
    │
    ▼
UI refreshes IP address table
UI shows success message
```

### Auto-Discovery Flow

#### Accept Discovered CI Flow

```
User views discovered CI queue
User clicks "Accept" on a discovered CI
    │
    ▼
POST /api/v0.1/ad/accept
    │
    Body: { adc_id: 123 }
    │
    ▼
API: AutoDiscoveryCICRUD.accept()
    │
    ├── Get discovered CI from queue
    ├── Get discovery rule (AutoDiscoveryCIType)
    ├── Map discovery keys to CI attributes
    ├── Apply value mappings (cloud providers)
    ├── CIManager.add() - Create actual CI
    │
    ├── If CI type is IPAM_ADDRESS:
    │   └── Auto-assign IP to subnet
    │       ├── Find subnet by subnet_id/cidr/vlan
    │       └── IpAddressManager.assign_ips()
    │
    ├── Trigger async task:
    │   └── build_relations_for_ad_accept()
    │       ├── Get relationship rules
    │       ├── Find peer CIs
    │       ├── Create relationships
    │       └── Handle is_reverse flag
    │
    └── Mark discovered CI as accepted
    │
    ▼
Return success
    │
    ▼
UI removes CI from queue
UI shows success message
```

#### Discovery Rule Sync Flow

```
External client requests rules
    │
    ▼
GET /api/v0.1/ad/rule?ci_id=123&oneagent_id=0x1&last_update_at=...
    │
    ▼
API: AutoDiscoveryCITypeCRUD.get()
    │
    ├── Get all enabled rules
    ├── Filter by agent_id or query_expr
    ├── Decrypt credentials if needed
    ├── Calculate last_update_at
    └── Return applicable rules
    │
    ▼
Client receives rules
Client executes discovery
Client sends discovered data
    │
    ▼
POST /api/v0.1/ad/ingest
    │
    Body: { ci_type_name: "server", data: {...}, ... }
    │
    ▼
API: IngestView.post()
    │
    ├── Validate signature
    ├── Store in ad_cis table
    ├── Status: QUEUED
    └── Return success
    │
    ▼
Discovered CI appears in queue
```

### Permission Check Flow

#### Component Permission Check

```
Component mounts
    │
    ▼
Check Vuex store for user permissions
    │
    ├── Has permission
    │   └── Render component
    │
    └── No permission
        └── Show "No Permission" page
```

#### API Permission Check

```
API request arrives
    │
    ▼
@validate_permission decorator
    │
    ▼
ACLManager.has_permission()
    │
    ├── Check if app admin
    │   └── Bypass all checks
    │
    ├── Get user's role
    ├── Get role's parent roles (recursive)
    ├── Check resource permissions
    │   ├── Direct resource permissions
    │   └── Resource group permissions
    │
    ├── Has permission
    │   └── Process request
    │
    └── No permission
        └── Return 403 Forbidden
```

### Cache Update Flow

```
CI is updated
    │
    ▼
CIManager.update()
    │
    ├── Update database
    └── Trigger Celery task: ci_cache
        │
        ▼
Background task: ci_cache()
    │
    ├── Get updated CI from database
    ├── Format CI data
    │
    ├── If USE_ES:
    │   └── es.create_or_update(ci_id, ci_dict)
    │
    └── Else:
        └── rd.create_or_update({ci_id: json.dumps(ci_dict)})
    │
    ├── Build relationships
    └── Fire triggers
```

---

## IPAM Module

### Subnet Hierarchy

```
Scope (Root)
    │
    ├── Region
    │   │
    │   └── Subnet (10.0.0.0/16)
    │       │
    │       ├── Subnet (10.0.0.0/24)
    │       │   ├── IP: 10.0.0.1
    │       │   ├── IP: 10.0.0.2
    │       │   └── ...
    │       │
    │       └── Subnet (10.0.1.0/24)
    │           └── ...
    │
    └── Subnet (192.168.0.0/16)
        └── ...
```

### Subnet Attributes

- `cidr`: Subnet CIDR notation (e.g., "10.0.0.0/24")
- `hosts_count`: Total available IP addresses
- `assign_count`: Number of assigned IPs
- `used_count`: Number of used IPs
- `free_count`: Number of free IPs

### IP Address Attributes

- `ip`: IP address value
- `assign_status`: ASSIGN, USED, FREE
- `is_used`: Boolean flag

### Tree View Algorithm

1. Fetch all subnets with `SearchFromDB`
2. Build parent-child relationships from `CIRelation`
3. Sort by `_id` (cast to int for consistency)
4. Return hierarchical tree structure

### Statistics Calculation

1. Find leaf nodes (subnets without children)
2. Aggregate statistics from leaf nodes
3. Calculate totals: address_num, address_free_num, address_assign_num, address_used_num

---

## Security & Permissions

### Permission Model

**Resource Types** (from `ResourceTypeEnum`):
- `CIType`: CI type configuration
- `CITypeRelation`: CI type relationship
- `CI`: Individual CI access
- `RelationView`: Relationship view
- `TopologyView`: Topology view
- `CIFilter`: CI filter access
- `PAGE`: Page access

**Permissions** (from `PermEnum`):
- `create`: Create resource
- `update`: Update resource
- `delete`: Delete resource
- `read`: Read resource
- `config`: Configure resource
- `grant`: Grant permissions

### ACL (Access Control List) Architecture

#### ACL Application Concept

**ACL Application** là một khái niệm cốt lõi để phân tách và quản lý permissions theo từng ứng dụng trong hệ thống multi-application.

**App Model** (`api/models/acl.py`):
```python
class App(Model):
    __tablename__ = "acl_apps"
    
    name = db.Column(db.String(64), index=True)  # Tên ứng dụng, ví dụ: 'cmdb'
    description = db.Column(db.Text)            # Mô tả application
    app_id = db.Column(db.Text)                 # External app ID (dùng cho API auth)
    secret_key = db.Column(db.Text)             # Secret key cho API authentication
```

**Mục đích của ACL Application**:

1. **Phân tách Resources**: 
   - Mỗi application có resources riêng
   - Resources được scope bởi `app_id`
   - Ví dụ: Resource "server" trong app "cmdb" khác với "server" trong app khác

2. **Phân tách Roles**: 
   - Mỗi application có roles riêng
   - Roles được scope bởi `app_id`
   - Có thể có global roles (app_id = NULL)

3. **Phân tách Permissions**: 
   - Permissions được quản lý theo application
   - Resource types được định nghĩa theo application

4. **Isolation**: 
   - Dữ liệu permissions giữa các applications được tách biệt hoàn toàn
   - Tránh conflict giữa các applications

5. **API Authentication**:
   - `app_id` và `secret_key` dùng để authenticate giữa các services
   - Generate JWT token cho inter-service communication

**Trong CMDB System**:

- **Application mặc định**: `'cmdb'`
- Tất cả resources, roles, permissions của CMDB đều thuộc `app_id` của application 'cmdb'
- Cho phép hệ thống hỗ trợ nhiều applications khác nhau trên cùng một ACL framework

**Database Schema**:
```sql
-- Tất cả ACL tables đều có app_id foreign key
acl_resources.app_id -> acl_apps.id
acl_roles.app_id -> acl_apps.id
acl_resource_types.app_id -> acl_apps.id
acl_role_permissions.app_id -> acl_apps.id
acl_role_relations.app_id -> acl_apps.id
```

**Ví dụ sử dụng**:
```python
# Khởi tạo ACLManager cho application 'cmdb'
acl_manager = ACLManager(app='cmdb')  # Default là 'cmdb'

# Tất cả operations sẽ scope trong application 'cmdb'
acl_manager.add_resource('server', ResourceTypeEnum.CI)
acl_manager.grant_resource_to_role('server', 'admin', ResourceTypeEnum.CI, [PermEnum.READ])

# Permission check cũng scope trong application
has_perm = acl_manager.has_permission('server', ResourceTypeEnum.CI, PermEnum.READ)
```

**App Admin**:
- Mỗi application có thể có app admin role
- App admin bypass tất cả permission checks trong application đó
- Check: `is_app_admin(app_id)`

**Multi-Application Support**:
- Hệ thống có thể có nhiều applications: 'cmdb', 'oneterm', 'messenger', etc.
- Mỗi application quản lý permissions độc lập
- User có thể có roles trong nhiều applications khác nhau

#### Core Components

**1. ACLManager** (`api/lib/perm/acl/acl.py`)
- Main entry point for permission checking
- **Initialized with app parameter**: `ACLManager(app='cmdb')`
- Manages resources, roles, and permissions **within the specified application**
- Methods:
  - `add_resource()`: Register new resource (scoped to app)
  - `grant_resource_to_role()`: Grant permissions to role (scoped to app)
  - `revoke_resource_from_role()`: Revoke permissions (scoped to app)
  - `has_permission()`: Check if user/role has permission (scoped to app)

**2. Permission Checking Flow**

```python
# Permission check flow (from acl.py:156-165)
def has_permission(resource_name, resource_type, perm, resource_id=None, rid=None):
    # 1. Check if user is app admin (bypass all checks)
    if is_app_admin(self.app_id):
        return True
    
    # 2. Get user's role
    role = self._get_role(current_user.username) if rid is None else RoleCache.get(rid)
    
    # 3. Check permission recursively through role hierarchy
    return RoleCRUD.has_permission(role.id, resource_name, resource_type, 
                                   self.app_id, perm, resource_id=resource_id)
```

**3. Role Hierarchy** (`api/lib/perm/acl/role.py`)

- **Parent-Child Relationships**: Roles can have parent roles
- **Permission Inheritance**: Child roles inherit permissions from parents
- **Recursive Permission Check**: 
  ```python
  # From role.py:419-443
  def has_permission(rid, resource_name, resource_type_name, app_id, perm, resource_id=None):
      # Get all parent role IDs recursively
      parent_ids = RoleRelationCRUD.recursive_parent_ids(rid, app_id)
      
      # Get resource groups
      group_ids = cls.get_group_ids(resource_id)
      
      # Check permissions in parent roles
      for parent_id in parent_ids:
          id2perms = RoleRelationCache.get_resources(parent_id, app_id)
          
          # Check direct resource permissions
          perms = id2perms['id2perms'].get(resource_id, [])
          if perms and {perm}.issubset(set(perms)):
              return True
          
          # Check resource group permissions
          for group_id in group_ids:
              perms = id2perms['group2perms'].get(group_id, [])
              if perms and {perm}.issubset(set(perms)):
                  return True
      
      return False
  ```

**4. Resource Groups**

- Resources can be grouped for easier permission management
- Group permissions apply to all resources in the group
- Supports hierarchical resource organization

**5. Permission Caching** (`api/lib/perm/acl/cache.py`)

**RoleRelationCache**: Caches role relationships and permissions
- `PREFIX_PARENT`: Parent role IDs
- `PREFIX_CHILDREN`: Child role IDs  
- `PREFIX_RESOURCES`: Resource permissions (`id2perms`, `group2perms`)
- Cache rebuild on permission changes

**Cache Structure**:
```python
# From cache.py:183-198
def get_resources(rid, app_id, force=False):
    """
    Returns: {
        'id2perms': {resource_id: [perm1, perm2, ...]},
        'group2perms': {group_id: [perm1, perm2, ...]}
    }
    """
    resources = cache.get(cls.PREFIX_RESOURCES.format(rid, app_id))
    if not resources or force:
        resources = RoleCRUD.get_resources(rid, app_id)
        if resources['id2perms'] or resources['group2perms']:
            cache.set(cls.PREFIX_RESOURCES.format(rid, app_id), resources, timeout=0)
    return resources or {}
```

**6. Permission Validation Decorator**

```python
# From acl.py:216-227
def validate_permission(resources, resource_type, perm, app=None):
    if not resources:
        return
    
    if current_app.config.get("USE_ACL"):
        if current_user.username == "worker":  # Background worker bypass
            return
        
        resources = [resources] if isinstance(resources, str) else resources
        for resource in resources:
            if not ACLManager(app).has_permission(resource, resource_type, perm):
                return abort(403, ErrFormat.resource_no_permission.format(resource, perm))
```

**7. CI-Level Permissions**

- **Filter Permissions**: Users can only see CIs they have permission to view
- **CIFilterPermsCRUD**: Manages CI-level filter permissions
- Applied during search operations

### Authentication Methods

1. **Session-based**: Flask-Login with session cookies
2. **API Key**: For programmatic access (`AuthWithKeyView`)
3. **OAuth2**: For third-party integrations (`OAuth2`)
4. **CAS**: Single Sign-On support (`CAS`)
5. **Token-based**: Access token for ACL service integration

### Security Features

1. **SQL Injection Prevention**: Query validation in search engine
2. **Table Name Whitelist**: Only allowed tables in queries
3. **Query Length Limit**: 200,000 characters max
4. **Dangerous Pattern Detection**: Blocks dangerous SQL patterns
5. **Worker User Bypass**: Background tasks use "worker" user

---

## Caching Strategy

### Redis Cache Structure

#### CI Type Cache
- Key: `cmdb:ci_type:{type_id}`
- TTL: No expiration (invalidated on update)

#### Attribute Cache
- Key: `cmdb:attribute:{attr_id}`
- TTL: No expiration (invalidated on update)

#### CI Relation Cache
- Key: `cmdb:ci_relation:{ci_id}`
- Format: JSON with `{ci_id: type_id}` mappings
- TTL: No expiration (invalidated on update)

#### Auto-Discovery Mapping Cache
- Key: `cmdb:ad_mapping:{rule_id}`
- TTL: No expiration (invalidated on update)

### Cache Invalidation

- On CI create/update/delete
- On CI type create/update/delete
- On relationship create/delete
- On attribute update

---

## Redis Cache vs Elasticsearch

### So sánh tổng quan

| Đặc điểm | Redis Cache | Elasticsearch |
|----------|-------------|---------------|
| **Mục đích** | Cache layer cho fast lookup | Search engine cho full-text search |
| **Bắt buộc** | ✅ Required (luôn được sử dụng) | ❌ Optional (chỉ khi USE_ES=True) |
| **Data Structure** | Key-Value, Hash maps | Document-based, Inverted index |
| **Storage Type** | In-memory cache | Persistent search index |
| **Primary Use** | Fast CI retrieval by ID | Complex search queries |
| **Search Capability** | ❌ Không hỗ trợ search | ✅ Full-text search, faceted search |
| **Performance** | Very fast (in-memory) | Fast (optimized for search) |

### Mục đích sử dụng khác nhau

#### Redis Cache

**1. CI Data Cache** (`REDIS_PREFIX_CI`):
```python
# From tasks/cmdb.py:52
# Structure: {ci_id: json.dumps(ci_dict)}
rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)
```
- **Mục đích**: Cache toàn bộ CI data để tránh query database
- **Format**: JSON string của CI dictionary
- **Lookup**: O(1) - rất nhanh khi biết CI ID
- **Khi nào dùng**: Khi `USE_ES = False` (default)

**2. CI Relation Cache** (`REDIS_PREFIX_CI_RELATION`):
```python
# Structure: {ci_id: json.dumps({peer_ci_id: type_id, ...})}
rd.create_or_update(relations, REDIS_PREFIX_CI_RELATION)
```
- **Mục đích**: Cache relationships để traverse nhanh
- **Format**: JSON với `{ci_id: type_id}` mappings
- **Use case**: Tree view, relationship traversal

**3. Metadata Cache**:
- `CITypeCache`: CI type definitions
- `AttributeCache`: Attribute definitions
- `CITypeAttributesCache`: CI type attribute mappings
- **Mục đích**: Tránh query database cho metadata

#### Elasticsearch

**1. Search Index**:
```python
# From tasks/cmdb.py:49-50
if current_app.config.get("USE_ES"):
    es.create_or_update(ci_id, ci_dict)
```
- **Mục đích**: Index CI data để search
- **Format**: Document với tất cả attributes as fields
- **Lookup**: Không phải primary use case
- **Khi nào dùng**: Khi `USE_ES = True`

**2. Search Operations**:
- Full-text search với Chinese support
- Faceted search (aggregations)
- Complex queries (AND, OR, NOT, ranges)
- **Mục đích**: Tìm kiếm CIs dựa trên attributes

### Data Flow Comparison

#### Khi USE_ES = False (Default)

```
CI Create/Update
    │
    ▼
Database (MySQL)
    │
    ├── Store in c_cis, c_ci_attributes
    │
    └── Trigger Celery task: ci_cache
        │
        ▼
    Redis Cache
    └── Store: {ci_id: json.dumps(ci_dict)}
        │
        ▼
    Search Request
        │
        ▼
    Database Search (SearchFromDB)
    └── Query MySQL directly
```

#### Khi USE_ES = True

```
CI Create/Update
    │
    ▼
Database (MySQL)
    │
    ├── Store in c_cis, c_ci_attributes
    │
    └── Trigger Celery task: ci_cache
        │
        ├── Elasticsearch Index
        │   └── Store: Document with all attributes
        │
        └── Redis Cache (vẫn được dùng cho metadata)
            └── Store: CI types, attributes, relations
        │
        ▼
    Search Request
        │
        ▼
    Elasticsearch Search (SearchFromES)
    └── Query ES index
```

### Cấu trúc dữ liệu

#### Redis Cache Structure

**CI Cache**:
```python
# Key: REDIS_PREFIX_CI (e.g., "cmdb:ci")
# Value: Hash map
{
    "123": '{"_id": 123, "_type": "server", "hostname": "web01", ...}',
    "124": '{"_id": 124, "_type": "server", "hostname": "web02", ...}',
    ...
}
```

**Relation Cache**:
```python
# Key: REDIS_PREFIX_CI_RELATION
# Value: Hash map
{
    "123": '{"456": 10, "789": 10}',  # CI 123 has relations to CI 456, 789 (type_id=10)
    ...
}
```

**Metadata Cache**:
```python
# Key: "CIType::ID::10"
# Value: CIType object (serialized)
```

#### Elasticsearch Document Structure

**CI Document**:
```json
{
    "_id": "auto-generated",
    "_source": {
        "ci_id": 123,
        "_type": "server",
        "type_id": 10,
        "hostname": "web01",
        "ip": "10.0.0.1",
        "status": "VALIDATE",
        "created_at": "2025-12-04 10:00:00",
        ... (all attributes as fields)
    }
}
```

### Khi nào dùng cái nào?

#### Redis Cache (Luôn được dùng)

**Use Cases**:
1. ✅ **Fast CI lookup by ID**: `get_ci_by_id()` - rất nhanh
2. ✅ **Metadata caching**: CI types, attributes, relations
3. ✅ **Relationship traversal**: Tree view, relationship queries
4. ✅ **Session storage**: User sessions, temporary data
5. ✅ **Rate limiting**: API rate limiting counters

**Không dùng cho**:
- ❌ Search operations (không có search capability)
- ❌ Complex queries (chỉ lookup by key)

#### Elasticsearch (Optional)

**Use Cases**:
1. ✅ **Full-text search**: Tìm kiếm theo text content
2. ✅ **Complex queries**: AND, OR, NOT, ranges, wildcards
3. ✅ **Faceted search**: Aggregations, statistics
4. ✅ **Chinese text search**: Với IK analyzer
5. ✅ **Large-scale search**: >100,000 CIs

**Không dùng cho**:
- ❌ Simple lookup by ID (Redis nhanh hơn)
- ❌ Metadata caching (Redis đủ)
- ❌ Small deployments (<10,000 CIs)

### Performance Comparison

#### Redis Cache

**Strengths**:
- ⚡ **Extremely fast**: In-memory, O(1) lookup
- 💾 **Low memory overhead**: Chỉ cache cần thiết
- 🔄 **Simple**: Key-value operations
- 📦 **Lightweight**: Không cần infrastructure phức tạp

**Limitations**:
- ❌ **No search**: Chỉ lookup by key
- ❌ **Memory limit**: Phụ thuộc vào RAM
- ❌ **No complex queries**: Không hỗ trợ query language

#### Elasticsearch

**Strengths**:
- 🔍 **Powerful search**: Full-text, faceted, complex queries
- 📊 **Analytics**: Aggregations, statistics
- 🌐 **Scalable**: Cluster support, sharding
- 🔤 **Text analysis**: IK analyzer cho Chinese

**Limitations**:
- ⚠️ **Slower than Redis**: Disk-based, query processing
- 💰 **Resource intensive**: Cần nhiều RAM và disk
- 🔧 **Complex setup**: Cần maintain cluster
- 📈 **Overhead**: Index maintenance, mapping updates

### Code Examples

#### Redis Usage

```python
# Get CI by ID (fast lookup)
ci_dict = rd.get([ci_id], REDIS_PREFIX_CI)[0]
if ci_dict:
    ci_dict = json.loads(ci_dict)
else:
    # Fallback to database
    ci_dict = get_ci_from_db(ci_id)
    rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)

# Get CI type (metadata cache)
ci_type = CITypeCache.get(type_id)
if not ci_type:
    ci_type = CIType.get_by_id(type_id)
    CITypeCache.set(ci_type)
```

#### Elasticsearch Usage

```python
# Search CIs (complex query)
query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"_type": "server"}},
                {"wildcard": {"hostname": "web*"}}
            ]
        }
    }
}
numfound, results, aggregations = es.read(query)

# Get CI by ID (not recommended, use Redis instead)
query = {"query": {"term": {"ci_id": 123}}}
numfound, results, _ = es.read(query)
```

### Decision Matrix

| Scenario | Redis | Elasticsearch |
|----------|-------|---------------|
| Lookup CI by ID | ✅ Use | ❌ Don't use |
| Search by attributes | ❌ Can't | ✅ Use |
| Full-text search | ❌ Can't | ✅ Use |
| Metadata cache | ✅ Use | ❌ Don't use |
| Relationship traversal | ✅ Use | ❌ Don't use |
| Faceted search | ❌ Can't | ✅ Use |
| Small dataset (<10K CIs) | ✅ Sufficient | ⚠️ Overkill |
| Large dataset (>100K CIs) | ✅ Still use | ✅ Recommended |
| Chinese text search | ❌ Can't | ✅ Use |

### Best Practices

1. **Always use Redis**: Cho metadata và fast lookup
2. **Use Elasticsearch when**:
   - Cần advanced search features
   - Dataset lớn (>100K CIs)
   - Cần Chinese text search
   - Cần faceted search/analytics
3. **Don't use Elasticsearch for**:
   - Simple ID lookup (Redis nhanh hơn)
   - Metadata caching (Redis đủ)
   - Small deployments (overhead không đáng)

---

## Elasticsearch Configuration

### Overview

Elasticsearch là một tùy chọn (optional) cho search engine trong CMDB, cung cấp full-text search và hiệu năng tốt hơn cho large-scale searches. Hệ thống có thể hoạt động với hoặc không có Elasticsearch.

### Configuration

#### 1. Settings Configuration (`settings.py`)

```python
# Elasticsearch Configuration
ES_HOST = '127.0.0.1'           # Elasticsearch server host
ES_PORT = 9200                  # Elasticsearch server port (default: 9200)
ES_USER = None                  # Optional: Username for authentication
ES_PASSWORD = None              # Optional: Password for authentication
USE_ES = False                  # Enable/disable Elasticsearch (default: False)
```

**Environment Variables** (alternative):
- `ES_HOST`: Elasticsearch host
- `ES_PORT`: Elasticsearch port
- `ES_USER`: Elasticsearch username (optional)
- `ES_PASSWORD`: Elasticsearch password (optional)
- `USE_ES`: Enable Elasticsearch (True/False)

#### 2. Connection Setup

**ESHandler** (`api/lib/utils.py`):
```python
class ESHandler(object):
    def __init__(self, flask_app=None):
        self.index = "cmdb"  # Fixed index name
    
    def init_app(self, app):
        config = app.config
        
        # Build connection URI
        if config.get('ES_USER') and config.get('ES_PASSWORD'):
            # With authentication
            uri = "http://{}:{}@{}:{}/".format(
                config.get('ES_USER'),
                config.get('ES_PASSWORD'),
                config.get('ES_HOST'),
                config.get('ES_PORT'))
        else:
            # Without authentication
            uri = "{}:{}".format(
                config.get('ES_HOST'),
                config.get('ES_PORT') or 9200)
        
        # Create Elasticsearch client
        self.es = Elasticsearch(
            uri,
            timeout=10,                    # Request timeout
            max_retries=3,                 # Max retry attempts
            retry_on_timeout=True,         # Retry on timeout
            retry_on_status=(502, 503, 504, "N/A"),  # Retry on these status codes
            maxsize=10                     # Connection pool size
        )
        
        # Auto-create index if not exists
        try:
            if not self.es.indices.exists(index=self.index):
                self.es.indices.create(index=self.index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error != 'resource_already_exists_exception':
                raise
```

#### 3. Index and Mapping

**Index Name**: `"cmdb"` (fixed, không thể thay đổi)

**Auto Mapping Update**:
- Mappings được tự động update khi attribute được tạo/update
- Command: `flask cmdb init-cache` để initialize mappings cho tất cả attributes

**Mapping Configuration**:
```python
# From api/commands/click_cmdb.py
for attr in attributes:
    other = dict()
    other['index'] = True if attr.is_index else False
    
    # Chinese text analyzer (IK plugin required)
    if attr.value_type == ValueTypeEnum.TEXT:
        other['analyzer'] = 'ik_max_word'      # Index analyzer
        other['search_analyzer'] = 'ik_smart'   # Search analyzer
        if attr.is_index:
            other["fields"] = {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
    
    # Update mapping
    es.update_mapping(attr.name, ValueTypeMap.es_type[attr.value_type], other)
```

**Value Type to ES Type Mapping**:
```python
ValueTypeMap.es_type = {
    ValueTypeEnum.INT: "long",
    ValueTypeEnum.FLOAT: "float",
    ValueTypeEnum.TEXT: "text",        # With IK analyzer
    ValueTypeEnum.DATETIME: "text",
    ValueTypeEnum.DATE: "text",
    ValueTypeEnum.TIME: "text",
    ValueTypeEnum.JSON: "object",
    ValueTypeEnum.BOOL: "boolean"
}
```

#### 4. CI Indexing

**Automatic Indexing**:
- CIs được tự động index vào Elasticsearch khi:
  - CI được tạo (create)
  - CI được cập nhật (update)
  - CI được xóa (delete - remove from index)

**Indexing Process**:
```python
# From tasks/cmdb.py
@celery.task(name="cmdb.ci_cache", queue=CMDB_QUEUE)
def ci_cache(ci_id, operate_type, record_id):
    # Get CI data from database
    ci_dict = m.get_ci_by_id_from_db(ci_id, need_children=False, use_master=False)
    
    # Index to Elasticsearch if enabled
    if current_app.config.get("USE_ES"):
        es.create_or_update(ci_id, ci_dict)
    else:
        # Fallback to Redis cache
        rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)
```

**Index Document Structure**:
- Document ID: Auto-generated by Elasticsearch
- Document Body: CI data dictionary (all attributes as fields)
- Special fields:
  - `ci_id`: CI ID (for lookup)
  - `ci_type`: CI type name
  - `type_id`: CI type ID

#### 5. Search Implementation

**Search Selection**:
```python
# From search/ci/__init__.py
def search(query=None, fl=None, facet=None, page=1, ...):
    if current_app.config.get("USE_ES"):
        s = SearchFromES(query, fl, facet, page, ret_key, count, sort)
    else:
        s = SearchFromDB(query, fl, facet, page, ret_key, count, sort, ...)
    return s
```

**Elasticsearch Search Features** (`api/lib/cmdb/search/ci/es/search.py`):
- **Query Language**: Same as DB search (`_type:server AND hostname:web*`)
- **Full-text Search**: With Chinese IK analyzer support
- **Faceted Search**: Aggregations for statistics
- **Range Queries**: `[value1_TO_value2]`, `>=value`, `<=value`
- **Wildcard Queries**: `hostname:web*`
- **Sorting**: Multiple field sorting
- **Pagination**: `from` and `size` parameters

**Query Building**:
```python
# Example ES query structure
{
    "query": {
        "bool": {
            "must": [        # AND conditions
                {"term": {"_type": "server"}},
                {"wildcard": {"hostname": "web*"}}
            ],
            "should": [],    # OR conditions
            "must_not": []   # NOT conditions
        }
    },
    "from": 0,
    "size": 20,
    "sort": [{"ci_id": {"order": "asc"}}]
}
```

#### 6. Installation and Setup

**1. Install Elasticsearch**:
```bash
# Download and install Elasticsearch 7.17.9
# https://www.elastic.co/downloads/elasticsearch

# Start Elasticsearch
./bin/elasticsearch
```

**2. Install IK Analyzer Plugin** (for Chinese text search):
```bash
# Install IK plugin
./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.17.9/elasticsearch-analysis-ik-7.17.9.zip

# Restart Elasticsearch
```

**3. Configure CMDB**:
```python
# In settings.py
ES_HOST = '127.0.0.1'
ES_PORT = 9200
USE_ES = True  # Enable Elasticsearch
```

**4. Initialize Index and Mappings**:
```bash
# Run initialization command
flask cmdb init-cache
```

**5. Re-index Existing CIs** (if needed):
```bash
# Re-index all existing CIs
flask cmdb reindex-all
```

#### 7. Monitoring and Maintenance

**Health Check**:
```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# Check index status
curl http://localhost:9200/cmdb/_stats
```

**Index Management**:
```bash
# Delete index (if needed to rebuild)
curl -X DELETE http://localhost:9200/cmdb

# Recreate index
flask cmdb init-cache
```

**Performance Tuning**:
- Adjust `maxsize` in ESHandler for connection pool
- Configure Elasticsearch heap size
- Use multiple Elasticsearch nodes for clustering
- Configure index refresh interval

#### 8. Advantages and Disadvantages

**Advantages**:
- ✅ Fast full-text search
- ✅ Better performance for large datasets
- ✅ Advanced search features (facets, aggregations)
- ✅ Chinese text search support (IK analyzer)
- ✅ Scalable with Elasticsearch clustering

**Disadvantages**:
- ❌ Additional infrastructure requirement
- ❌ Need to maintain Elasticsearch cluster
- ❌ Data synchronization overhead
- ❌ More complex deployment

**When to Use**:
- Large number of CIs (>100,000)
- Need advanced full-text search
- Need Chinese text search
- Need faceted search and aggregations

**When NOT to Use**:
- Small deployments (<10,000 CIs)
- Simple search requirements
- Limited infrastructure resources
- Prefer simpler architecture

---

## Deployment Architecture

### Production Deployment

```
┌─────────────────────────────────────────────────────┐
│                  Load Balancer                      │
│                  (Nginx/HAProxy)                    │
└───────────────┬───────────────────┬─────────────────┘
                │                   │
        ┌───────▼──────┐    ┌───────▼──────┐
        │  Flask API   │    │  Flask API   │
        │  (Gunicorn)  │    │  (Gunicorn)  │
        └───────┬──────┘    └───────┬──────┘
                │                   │
                └───────────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
│    MySQL     │    │    Redis     │    │   Celery     │
│  (Primary)   │    │   (Cache)    │    │   Workers    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Docker Deployment

```yaml
services:
  cmdb-api:
    build: ./cmdb-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://...
      - REDIS_URL=redis://...
  
  cmdb-ui:
    build: ./cmdb-ui
    ports:
      - "80:80"
  
  mysql:
    image: mysql:5.7
    volumes:
      - mysql_data:/var/lib/mysql
  
  redis:
    image: redis:6-alpine
  
  celery-worker:
    build: ./cmdb-api
    command: celery -A celery_worker.celery worker
```

### API Endpoints

**Auto-Discovery Endpoints**:
- `GET /api/v0.1/ad/rule`: Get discovery rules (supports incremental sync)
- `POST /api/v0.1/ad/ingest`: Ingest discovered CI data
- `GET /api/v0.1/ad/ci`: List discovered CIs in queue
- `POST /api/v0.1/ad/accept`: Accept discovered CI and create actual CI
- `POST /api/v0.1/ad/reject`: Reject discovered CI
- `GET /api/v0.1/adr`: List discovery rules (admin)
- `POST /api/v0.1/adr`: Create discovery rule (admin)

---

## Performance Considerations

### Database Optimization

#### 1. Indexes
**Critical Indexes** (from models):
- `c_cis.type_id` (indexed)
- `c_cis.deleted` (indexed)
- `c_ci_relations.first_ci_id` (indexed)
- `c_ci_relations.second_ci_id` (indexed)
- `c_ci_attributes.ci_id` (indexed)
- `c_ci_attributes.attr_id` (indexed)

#### 2. Query Optimization Techniques

**A. Query Batching for Large ID Lists**
```python
# From search.py:671-691
def _filter_ids(self, query_sql):
    if self.ci_ids:
        unique_ids = list(set(map(str, self.ci_ids)))
        
        # Batch processing for large ID lists (>1000)
        if len(unique_ids) > 1000:
            batch_size = 1000
            batches = []
            for i in range(0, len(unique_ids), batch_size):
                batch = unique_ids[i:i + batch_size]
                batches.append("IN_QUERY.ci_id IN ({})".format(",".join(batch)))
            
            # Use UNION to combine batches
            where_clause = " OR ".join(batches)
            return "SELECT * FROM ({0}) AS IN_QUERY WHERE {1}".format(
                query_sql, where_clause)
        else:
            return "SELECT * FROM ({0}) AS IN_QUERY WHERE IN_QUERY.ci_id IN ({1})".format(
                query_sql, ",".join(unique_ids))
```

**B. Query Length Management**
```python
# From search.py:137-139
# Increased limit to handle large number of CIs
if len(query_sql) > 200000:  # 200KB limit
    raise SearchError("Invalid query: query too long")
```

**C. Use Query Objects Instead of Lists**
```python
# From stats.py:33-34 (fixed)
# Before (WRONG): CI.get_by(type_id=...).filter(...)  # Returns list
# After (CORRECT):
ci_ids = [i.id for i in CI.get_by(only_query=True).filter(
    CI.type_id == self.subnet_type_id).filter(CI.deleted.is_(False)).all()]
```

**D. Field Filtering (fl parameter)**
- Only fetch required fields to reduce data transfer
- Example: `fl=['_id', 'hostname', 'ip']`

#### 3. SQL Injection Prevention
```python
# From search.py:97-139
def _validate_query_sql(self, query_sql):
    """
    Validate query SQL to prevent SQL injection
    """
    # 1. Check for dangerous patterns
    dangerous_patterns = [
        r'\b(DROP|DELETE|TRUNCATE|ALTER|CREATE|INSERT|UPDATE)\b',
        r'--', r'/\*', r'\*/', r';\s*;', r'UNION.*SELECT'
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, query_sql, re.IGNORECASE):
            raise SearchError("Invalid query: contains dangerous SQL patterns")
    
    # 2. Table name whitelist
    # Only allows tables starting with 'c_value_'
    if not table_name.startswith('c_value_'):
        raise SearchError(f"Invalid table name: {table_name}")
```

### Caching Strategy

#### 1. Multi-Level Caching

**A. Redis Cache** (`api/lib/cmdb/cache.py`)

**AttributeCache**:
```python
# Cache keys: Field::ID::{id}, Field::Name::{name}, Field::Alias::{alias}
# TTL: No expiration (invalidated on update)
```

**CITypeCache**:
```python
# Cache keys: CIType::ID::{id}, CIType::Name::{name}, CIType::Alias::{alias}
# TTL: No expiration (invalidated on update)
```

**CITypeAttributesCache**:
```python
# Cache keys: CITypeAttributes::TypeID::{type_id}
# Returns: List of CITypeAttribute objects
# TTL: No expiration (invalidated on update)
```

**B. Redis CI Cache** (`REDIS_PREFIX_CI`)
```python
# From tasks/cmdb.py:52
# Cache structure: {ci_id: json.dumps(ci_dict)}
# Used for fast CI retrieval without database query
rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)
```

**C. Redis CI Relation Cache** (`REDIS_PREFIX_CI_RELATION`)
```python
# Cache structure: {ci_id: json.dumps({peer_ci_id: type_id, ...})}
# Used for fast relationship traversal
# Format: JSON with {ci_id: type_id} mappings
```

#### 2. Cache Invalidation Strategy

**On CI Update**:
```python
# From tasks/cmdb.py:38-54
@celery.task
def ci_cache(ci_id, operate_type, record_id):
    # 1. Update Redis cache
    rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)
    
    # 2. Update Elasticsearch (if enabled)
    if current_app.config.get("USE_ES"):
        es.create_or_update(ci_id, ci_dict)
    
    # 3. Rebuild relationships
    CIRelationManager.build_by_attribute(ci_dict)
    
    # 4. Fire triggers
    CITriggerManager.fire(operate_type, payload, record_id)
```

**On CI Type/Attribute Update**:
- Clear `CITypeCache`
- Clear `CITypeAttributesCache`
- Clear `AttributeCache`

#### 3. ACL Permission Cache

**RoleRelationCache** (`api/lib/perm/acl/cache.py`):
```python
# Cache structure:
# - PREFIX_PARENT: Parent role IDs
# - PREFIX_CHILDREN: Child role IDs
# - PREFIX_RESOURCES: {id2perms: {...}, group2perms: {...}}
# TTL: No expiration (rebuild on permission change)
```

**Cache Rebuild**:
```python
# From cache.py:232-248
def rebuild(cls, rid, app_id):
    # Clear existing cache
    cls.clean(rid, app_id)
    
    # Rebuild parent/child relationships
    cls.get_parent_ids(rid, app_id, force=True)
    cls.get_child_ids(rid, app_id, force=True)
    
    # Rebuild resource permissions
    resources = cls.get_resources(rid, app_id, force=True)
    
    # Update HasResourceRoleCache
    if resources.get('id2perms') or resources.get('group2perms'):
        HasResourceRoleCache.add(rid, app_id)
```

### Search Performance

#### 1. Database Search (`SearchFromDB`)

**Query Building**:
- Uses UNION for multiple attribute queries
- Optimized JOIN operations
- Index usage for type_id and deleted filters

**Pagination**:
```python
# From search.py:43-55
def __init__(self, query=None, page=1, count=1, ...):
    self.page = page
    self.count = count
    # Uses LIMIT and OFFSET for pagination
```

**Field Filtering**:
- Only fetch required fields (`fl` parameter)
- Reduces data transfer and processing time

#### 2. Elasticsearch Search (Optional)

**Configuration** (`settings.py`):
```python
# Elasticsearch configuration
ES_HOST = '127.0.0.1'           # Elasticsearch host
ES_PORT = 9200                  # Elasticsearch port (default: 9200)
ES_USER = None                  # Optional: username for authentication
ES_PASSWORD = None              # Optional: password for authentication
USE_ES = False                  # Enable/disable Elasticsearch (default: False)
```

**ESHandler** (`api/lib/utils.py`):
```python
class ESHandler(object):
    def __init__(self, flask_app=None):
        self.index = "cmdb"  # Index name
    
    def init_app(self, app):
        # Build connection URI
        if config.get('ES_USER') and config.get('ES_PASSWORD'):
            uri = "http://{}:{}@{}:{}/".format(
                ES_USER, ES_PASSWORD, ES_HOST, ES_PORT)
        else:
            uri = "{}:{}".format(ES_HOST, ES_PORT or 9200)
        
        # Create Elasticsearch client
        self.es = Elasticsearch(uri,
                                timeout=10,
                                max_retries=3,
                                retry_on_timeout=True,
                                retry_on_status=(502, 503, 504, "N/A"),
                                maxsize=10)
        
        # Auto-create index if not exists
        if not self.es.indices.exists(index=self.index):
            self.es.indices.create(index=self.index)
```

**Enable/Disable**:
- Set `USE_ES = True` in `settings.py` to enable Elasticsearch
- System automatically switches between DB search and ES search:
  ```python
  # From search/ci/__init__.py
  if current_app.config.get("USE_ES"):
      s = SearchFromES(query, fl, facet, page, ret_key, count, sort)
  else:
      s = SearchFromDB(query, fl, facet, page, ret_key, count, sort, ...)
  ```

**Index Management**:
- **Index Name**: `"cmdb"` (fixed)
- **Auto-create**: Index is created automatically on first use
- **Mapping**: Field mappings are updated automatically when attributes are created/updated

**Field Mapping** (`api/commands/click_cmdb.py`):
```python
# Auto-update mapping for attributes
for attr in attributes:
    other = dict()
    other['index'] = True if attr.is_index else False
    
    if attr.value_type == ValueTypeEnum.TEXT:
        other['analyzer'] = 'ik_max_word'      # Chinese analyzer
        other['search_analyzer'] = 'ik_smart'  # Chinese search analyzer
        if attr.is_index:
            other["fields"] = {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
    
    es.update_mapping(attr.name, ValueTypeMap.es_type[attr.value_type], other)
```

**Value Type Mapping** (`api/lib/cmdb/utils.py`):
```python
ValueTypeMap.es_type = {
    ValueTypeEnum.INT: "integer",
    ValueTypeEnum.FLOAT: "float",
    ValueTypeEnum.TEXT: "text",
    ValueTypeEnum.DATETIME: "date",
    ValueTypeEnum.DATE: "date",
    ValueTypeEnum.TIME: "date",
    ValueTypeEnum.JSON: "object",
    ValueTypeEnum.BOOL: "boolean"
}
```

**CI Indexing**:
- CIs are automatically indexed when created/updated/deleted
- Indexing happens in background Celery task:
  ```python
  # From tasks/cmdb.py
  @celery.task
  def ci_cache(ci_id, operate_type, record_id):
      ci_dict = m.get_ci_by_id_from_db(ci_id, ...)
      
      if current_app.config.get("USE_ES"):
          es.create_or_update(ci_id, ci_dict)
      else:
          rd.create_or_update({ci_id: json.dumps(ci_dict)}, REDIS_PREFIX_CI)
  ```

**Search Features**:
- Full-text search with Chinese support (IK analyzer)
- Faceted search (aggregations)
- Range queries
- Wildcard queries
- Sorting
- Pagination

**Initialization Command**:
```bash
# Initialize Elasticsearch index and mappings
flask cmdb init-cache
```

**Requirements**:
- Elasticsearch 7.17.9
- IK Analyzer plugin (for Chinese text search)
- Python package: `elasticsearch==7.17.9`

#### 3. Search Query Optimization

**Type Filtering First**:
```python
# Always filter by type_id first (uses index)
# Then apply attribute filters
query = "_type:server AND hostname:web*"
```

**Avoid N+1 Queries**:
- Batch CI attribute fetching
- Use JOIN instead of multiple queries

### Background Processing

#### 1. Celery Tasks

**CI Cache Update** (`ci_cache`):
```python
# Async task to update cache after CI modification
@celery.task(name="cmdb.ci_cache", queue=CMDB_QUEUE)
def ci_cache(ci_id, operate_type, record_id):
    # Update Redis/ES cache
    # Fire triggers
    # Rebuild relationships
```

**Relationship Building** (`build_relations_for_ad_accept`):
```python
# Async task to build relationships after auto-discovery accept
@celery.task(name="cmdb.build_relations_for_ad_accept", queue=CMDB_QUEUE)
def build_relations_for_ad_accept(adc_dict, ci_id, ad_key2attr):
    # Build relationships based on discovery rules
    # Process in background to avoid blocking
```

**Batch CI Cache** (`batch_ci_cache`):
```python
# Batch update multiple CIs
# Used for attribute index updates
```

#### 2. Task Queue Configuration

- **Queue**: `CMDB_QUEUE` (configurable)
- **Concurrency**: Configurable via Celery workers
- **Retry**: Automatic retry on failure
- **Priority**: High priority for critical operations

### Performance Metrics

#### 1. Query Performance
- **Search Time**: Logged in `current_app.logger.debug("search time is: {0}".format(time.time() - start))`
- **Target**: < 1 second for typical queries
- **Optimization**: Index usage, query batching, caching

#### 2. Cache Hit Rate
- Monitor Redis cache hit rate
- Target: > 80% for frequently accessed data
- Cache warming on startup (optional)

#### 3. Background Task Processing
- Monitor Celery task queue length
- Alert on queue backlog
- Scale workers based on load

### Best Practices

1. **Always use `only_query=True`** for SQLAlchemy queries that need filtering
2. **Batch operations** for large datasets (>1000 items)
3. **Use field filtering** (`fl` parameter) to reduce data transfer
4. **Cache frequently accessed data** (CI types, attributes, permissions)
5. **Use async tasks** for heavy operations (relationship building, cache updates)
6. **Monitor query length** and batch large ID lists
7. **Index critical columns** (type_id, deleted, ci_id, attr_id)
8. **Use pagination** for large result sets

---

## Future Enhancements

### Planned Features

1. **GraphQL API**: Alternative to REST API
2. **Real-time Updates**: WebSocket support for live updates
3. **Advanced Analytics**: Dashboard and reporting
4. **Multi-tenancy**: Support for multiple organizations
5. **API Gateway**: Centralized API management
6. **Event-driven Architecture**: Event sourcing for audit trail
7. **Microservices**: Split into smaller services
8. **Kubernetes Support**: Native K8s resource discovery

### Technical Debt

1. **Test Coverage**: Increase unit and integration test coverage
2. **Documentation**: API documentation with OpenAPI/Swagger
3. **Monitoring**: APM and logging improvements
4. **Error Handling**: Standardized error responses
5. **Migration Tools**: Better database migration tooling

---

## Appendix

### A. Glossary

- **CI**: Configuration Item - Any IT resource managed in CMDB
- **CI Type**: Template/schema for a type of CI
- **Attribute**: Property of a CI (e.g., hostname, IP address)
- **Relationship**: Connection between two CIs
- **IPAM**: IP Address Management
- **DCIM**: Data Center Infrastructure Management
- **Auto-Discovery**: Automatic detection and ingestion of IT resources

### B. References

- [CMDB API Documentation](cmdb_api.md)
- [CMDB Query API](cmdb_query_api.md)
- [Contributing Guide](CONTRIBUTING.md)

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-04 | CMDB Team | Initial TDD |

---

**Document Status**: Draft  
**Last Updated**: 2025-12-04  
**Next Review**: 2026-01-04

