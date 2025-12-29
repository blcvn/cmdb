# Advanced Matching Rules cho CITypeRelation

## Tổng quan

Tính năng này cho phép cấu hình các cách matching phức tạp hơn khi tự động tạo relationship giữa các CI dựa trên attribute values. Thay vì chỉ so khớp chính xác (equals), bạn có thể sử dụng các operator khác như contains, in_list, has_one, và compare.

## Cấu trúc matching_rules

`matching_rules` là một JSON array, mỗi object đại diện cho một rule matching cho một cặp attribute:

```json
[
  {
    "parent_attr_id": 1,
    "child_attr_id": 2,
    "operator": "contains",
    "separator": ","
  }
]
```

### Các trường:

- `parent_attr_id`: ID của attribute trong parent CI type
- `child_attr_id`: ID của attribute trong child CI type
- `operator`: Loại matching operator (xem bên dưới)
- `separator`: (Optional) Ký tự phân cách chung cho cả parent và child, mặc định là `,`
- `parent_separator`: (Optional) Ký tự phân cách riêng cho parent value, nếu không có sẽ dùng `separator`
- `child_separator`: (Optional) Ký tự phân cách riêng cho child value, nếu không có sẽ dùng `separator`

## Các Matching Operators

### 1. `equals` (Mặc định)

So khớp chính xác giá trị.

**Ví dụ:**
- Parent: `name = "DC-01"`
- Child: `datacenter_name = "DC-01"`
- Kết quả: Match ✓

**Khi nào dùng:** Khi giá trị phải khớp chính xác.

### 2. `contains`

Kiểm tra xem parent value có chứa child value không (case-insensitive).

**Ví dụ:**
- Parent: `description = "Datacenter in Singapore"`
- Child: `location = "Singapore"`
- Kết quả: Match ✓ (vì "Datacenter in Singapore" chứa "Singapore")

**Khi nào dùng:** Khi parent có thể chứa nhiều thông tin, trong đó có giá trị của child.

### 3. `in_list`

Cả parent và child đều là danh sách (string được phân cách bởi separator), kiểm tra có phần tử chung không.

**Ví dụ 1: Cùng separator**
- Parent: `tags = "web,db,cache"`
- Child: `services = "web,api"`
- Separator: `,`
- Kết quả: Match ✓ (vì cả hai đều có "web")

**Ví dụ 2: Separator khác nhau**
- Parent: `tags = "web|db|cache"` (separator: `|`)
- Child: `services = "web,api"` (separator: `,`)
- Parent separator: `|`
- Child separator: `,`
- Kết quả: Match ✓ (vì cả hai đều có "web")

**Khi nào dùng:** Khi cả hai attribute đều là danh sách và bạn muốn tìm phần tử chung. Hữu ích khi parent và child sử dụng separator khác nhau.

### 4. `has_one`

Parent có một trong các giá trị của child (child là danh sách).

**Ví dụ 1: Cùng separator**
- Parent: `environment = "production"`
- Child: `environments = "dev,staging,production"`
- Separator: `,`
- Kết quả: Match ✓ (vì "production" có trong danh sách)

**Ví dụ 2: Separator khác nhau**
- Parent: `environment = "production"`
- Child: `environments = "dev|staging|production"` (separator: `|`)
- Child separator: `|`
- Kết quả: Match ✓ (vì "production" có trong danh sách)

**Khi nào dùng:** Khi parent có một giá trị đơn và child có danh sách các giá trị có thể. Hữu ích khi child sử dụng separator khác với mặc định.

### 5. `compare`

So sánh số (numeric comparison).

**Ví dụ:**
- Parent: `version = "2.5"`
- Child: `version = "2.50"`
- Kết quả: Match ✓ (vì 2.5 == 2.50)

**Khi nào dùng:** Khi cần so sánh số mà có thể có format khác nhau (ví dụ: "2.5" vs "2.50").

## Cách sử dụng qua API

### Tạo CITypeRelation với matching_rules

```bash
POST /api/v0.1/ci_type_relations/<parent_id>/<child_id>
```

**Body:**
```json
{
  "relation_type_id": 1,
  "constraint": "0",
  "parent_attr_ids": [1, 3],
  "child_attr_ids": [2, 4],
  "matching_rules": [
    {
      "parent_attr_id": 1,
      "child_attr_id": 2,
      "operator": "contains"
    },
    {
      "parent_attr_id": 3,
      "child_attr_id": 4,
      "operator": "in_list",
      "separator": "|"
    }
  ]
}
```

## Ví dụ thực tế

### Ví dụ 1: Server và Datacenter với contains

**Cấu hình:**
- Parent: Datacenter
- Child: Server
- Parent attribute: `description` (chứa location)
- Child attribute: `location`
- Operator: `contains`

**Khi tạo Server:**
- Server có `location = "Singapore"`
- Hệ thống tìm Datacenter có `description` chứa "Singapore"
- Tự động tạo relationship: Datacenter → Server

### Ví dụ 2: Application và Environment với has_one

**Cấu hình:**
- Parent: Environment
- Child: Application
- Parent attribute: `name` (single value: "production")
- Child attribute: `environments` (list: "dev,staging,production")
- Operator: `has_one`
- Separator: `,`

**Khi tạo Application:**
- Application có `environments = "dev,staging,production"`
- Hệ thống tìm Environment có `name` trong danh sách này
- Tự động tạo relationship: Environment → Application

### Ví dụ 3: Service và Tags với in_list

**Cấu hình:**
- Parent: Service
- Child: Tag
- Parent attribute: `tags` (list: "web,db,cache")
- Child attribute: `service_tags` (list: "web,api")
- Operator: `in_list`
- Separator: `,`

**Khi tạo Tag:**
- Tag có `service_tags = "web,api"`
- Hệ thống tìm Service có `tags` có phần tử chung
- Tự động tạo relationship: Service → Tag

## Lưu ý quan trọng

1. **Nếu không có matching_rules**: Hệ thống sẽ dùng operator mặc định `equals` cho tất cả các cặp attribute.

2. **Multiple attributes**: Nếu có nhiều cặp attribute, tất cả phải match thì relationship mới được tạo (AND logic).

3. **Performance**: Các operator như `contains`, `in_list`, `has_one` sẽ phải scan tất cả các CI để tìm match, nên có thể chậm hơn `equals`.

4. **Case sensitivity**: Operator `contains` là case-insensitive, các operator khác là case-sensitive.

5. **Null values**: Nếu parent hoặc child value là null, sẽ không match.

## Migration

Để thêm field `matching_rules` vào database, chạy SQL migration:

```sql
ALTER TABLE `c_ci_type_relations` 
ADD COLUMN `matching_rules` JSON NULL COMMENT 'Advanced matching rules for attribute-based relationships';
```

Hoặc sử dụng Alembic để tạo migration tự động.

