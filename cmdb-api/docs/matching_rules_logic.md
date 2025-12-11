# Logic Code Matching Rules - Giải thích chi tiết

## Tổng quan luồng xử lý

Logic matching rules được tích hợp vào quá trình tự động tạo relationship khi CI được tạo hoặc cập nhật. Dưới đây là chi tiết cách code hoạt động:

## 1. Entry Point - Khi CI được tạo/cập nhật

### Luồng chính:

```
CIManager.add() hoặc CIManager.update()
    ↓
ci_cache task (async Celery task)
    ↓
build_by_attribute() ← Logic matching được gọi ở đây
```

### Code trong `tasks/cmdb.py`:

```python
@celery.task(name="cmdb.ci_cache", queue=CMDB_QUEUE)
def ci_cache(ci_id, operate_type, record_id):
    # ... update cache/Elasticsearch ...
    
    # Gọi build_by_attribute để tự động tạo relationship
    ci_dict and CIRelationManager.build_by_attribute(ci_dict)
```

## 2. Core Logic - `build_by_attribute()`

### Vị trí: `api/lib/cmdb/ci.py` - dòng 1501-1598

### Luồng xử lý:

```
build_by_attribute(ci_dict)
    │
    ├── Tìm các CITypeRelation có parent_id = ci.type_id
    │   └── (CI này là parent, cần tìm children)
    │
    ├── Với mỗi CITypeRelation:
    │   ├── Lấy matching_rules từ database
    │   ├── Với mỗi cặp (parent_attr_id, child_attr_id):
    │   │   ├── _get_matching_rule() ← Tìm rule cho cặp này
    │   │   ├── Lấy operator, separator từ rule
    │   │   ├── Nếu operator = "equals":
    │   │   │   └── Query database trực tiếp (nhanh)
    │   │   └── Nếu operator khác:
    │   │       └── Scan tất cả child CIs và match
    │   └── Tạo relationship nếu match
    │
    └── Tìm các CITypeRelation có child_id = ci.type_id
        └── (CI này là child, cần tìm parents)
        └── Logic tương tự như trên
```

## 3. Helper Functions

### 3.1 `_get_matching_rule()` - Tìm rule cho cặp attribute

**Vị trí:** `api/lib/cmdb/ci.py` - dòng 1439-1447

```python
@staticmethod
def _get_matching_rule(matching_rules, parent_attr_id, child_attr_id):
    """Get matching rule for a pair of attributes"""
    if not matching_rules:
        return None
    for rule in matching_rules:
        if rule.get('parent_attr_id') == parent_attr_id and \
           rule.get('child_attr_id') == child_attr_id:
            return rule
    return None
```

**Chức năng:**
- Tìm trong `matching_rules` array rule tương ứng với cặp `(parent_attr_id, child_attr_id)`
- Trả về rule object hoặc None nếu không tìm thấy

### 3.2 `_match_values()` - So khớp giá trị theo operator

**Vị trí:** `api/lib/cmdb/ci.py` - dòng 1449-1499

```python
@staticmethod
def _match_values(parent_value, child_value, operator=None, 
                  separator=',', parent_separator=None, child_separator=None):
```

**Logic xử lý:**

1. **Kiểm tra null values:**
   ```python
   if parent_value is None or child_value is None:
       return False
   ```

2. **Xử lý separator:**
   ```python
   parent_sep = parent_separator if parent_separator is not None else separator
   child_sep = child_separator if child_separator is not None else separator
   ```

3. **Xử lý từng operator:**

   **a) EQUALS (mặc định):**
   ```python
   return str(parent_value) == str(child_value)
   ```

   **b) CONTAINS:**
   ```python
   parent_str = str(parent_value).lower()
   child_str = str(child_value).lower()
   return child_str in parent_str
   ```

   **c) IN_LIST:**
   ```python
   parent_list = [s.strip() for s in str(parent_value).split(parent_sep) if s.strip()]
   child_list = [s.strip() for s in str(child_value).split(child_sep) if s.strip()]
   return bool(set(parent_list) & set(child_list))  # Intersection
   ```

   **d) HAS_ONE:**
   ```python
   parent_str = str(parent_value).strip()
   child_list = [s.strip() for s in str(child_value).split(child_sep) if s.strip()]
   return parent_str in child_list
   ```

   **e) COMPARE:**
   ```python
   parent_num = float(parent_value)
   child_num = float(child_value)
   return parent_num == child_num
   ```

## 4. Chi tiết xử lý trong `build_by_attribute()`

### 4.1 Trường hợp CI là Parent (tìm children)

**Code:** dòng 1501-1550

```python
# 1. Tìm các CITypeRelation mà CI này là parent
child_items = CITypeRelation.get_by(parent_id=type_id, only_query=True)
    .filter(CITypeRelation.parent_attr_ids.isnot(None))

for item in child_items:
    relations = None
    matching_rules = item.matching_rules or []  # ← Lấy rules từ DB
    
    # 2. Với mỗi cặp attribute
    for parent_attr_id, child_attr_id in zip(item.parent_attr_ids, item.child_attr_ids):
        # 3. Lấy rule cho cặp này
        rule = cls._get_matching_rule(matching_rules, parent_attr_id, child_attr_id)
        operator = rule.get('operator') if rule else MatchingOperatorEnum.EQUALS
        separator = rule.get('separator', ',') if rule else ','
        parent_separator = rule.get('parent_separator') if rule else None
        child_separator = rule.get('child_separator') if rule else None
        
        # 4. Xử lý theo operator
        if operator == MatchingOperatorEnum.EQUALS:
            # Query trực tiếp (tối ưu)
            value_table = TableMap(attr=child_attr).table
            for child in value_table.get_by(attr_id=child_attr.id, 
                                          value=parent_attr_value, ...):
                _relations.add((ci_dict['_id'], child.ci_id))
        else:
            # Scan tất cả và match
            for child in value_table.get_by(...):
                if cls._match_values(parent_attr_value, child.value, 
                                   operator, separator, parent_separator, child_separator):
                    _relations.add((ci_dict['_id'], child.ci_id))
    
    # 5. Tạo relationships
    for parent_ci_id, child_ci_id in relations:
        cls.add(parent_ci_id, child_ci_id, ...)
```

### 4.2 Trường hợp CI là Child (tìm parents)

**Code:** dòng 1552-1598

Logic tương tự như trên nhưng đảo ngược:
- Tìm CITypeRelation có `child_id = type_id`
- So khớp ngược lại: `parent_attr_value` với `child_attr_value`
- Tạo relationship: `parent.ci_id → ci_dict['_id']`

## 5. Rebuild Logic - `rebuild_all_by_attribute()`

**Vị trí:** `api/lib/cmdb/ci.py` - dòng 1600-1650

**Khi nào được gọi:**
- Khi `matching_rules` được thay đổi trong CITypeRelation
- Task: `rebuild_relation_for_attribute_changed`

**Logic:**

```python
# 1. Lấy tất cả parent và child CIs
parent_values = parent_value_table.get_by(...)
child_values = child_value_table.get_by(...)

# 2. Nếu operator = EQUALS: dùng hash map (nhanh)
if operator == MatchingOperatorEnum.EQUALS:
    child_value2ci_ids = {}
    for child in child_values:
        child_value2ci_ids.setdefault(child.value, []).append(child.ci_id)
    
    for parent in parent_values:
        for child_ci_id in child_value2ci_ids.get(parent.value, []):
            _relations.add((parent.ci_id, child_ci_id))
else:
    # 3. Nếu operator khác: check tất cả combinations
    for parent in parent_values:
        for child in child_values:
            if cls._match_values(parent.value, child.value, operator, 
                               separator, parent_separator, child_separator):
                _relations.add((parent.ci_id, child.ci_id))
```

## 6. Tích hợp với API

### 6.1 Lưu matching_rules vào database

**File:** `api/lib/cmdb/ci_type.py` - `CITypeRelationManager.add()`

```python
@classmethod
def add(cls, parent, child, relation_type_id, constraint=...,
        parent_attr_ids=None, child_attr_ids=None, matching_rules=None):
    # ...
    existed = CITypeRelation.create(
        parent_id=p.id,
        child_id=c.id,
        parent_attr_ids=parent_attr_ids,
        child_attr_ids=child_attr_ids,
        matching_rules=matching_rules,  # ← Lưu vào DB
        ...
    )
```

### 6.2 API Endpoint nhận matching_rules

**File:** `api/views/cmdb/ci_type_relation.py`

```python
def post(self, parent_id, child_id):
    matching_rules = request.values.get("matching_rules")
    
    # Parse JSON nếu là string
    if matching_rules and isinstance(matching_rules, str):
        matching_rules = json.loads(matching_rules)
    
    CITypeRelationManager.add(..., matching_rules=matching_rules)
```

## 7. Ví dụ luồng xử lý cụ thể

### Scenario: Tạo Server mới với contains matching

**Input:**
- Server mới: `location = "Singapore"`
- CITypeRelation: Datacenter → Server
- Matching rule: `operator = "contains"`, `parent_attr_id = description`, `child_attr_id = location`

**Luồng xử lý:**

```
1. CIManager.add() tạo Server thành công
   ↓
2. ci_cache task được trigger
   ↓
3. build_by_attribute() được gọi với ci_dict của Server
   ↓
4. Tìm CITypeRelation có child_id = Server.type_id
   ↓
5. Tìm thấy rule: Datacenter → Server
   ↓
6. Lấy matching_rules: [{"operator": "contains", ...}]
   ↓
7. Với cặp (description, location):
   - parent_attr_value = ci_dict.get("location") = "Singapore"
   - operator = "contains"
   ↓
8. Scan tất cả Datacenter CIs:
   - Datacenter A: description = "Datacenter in Singapore" 
     → _match_values("Datacenter in Singapore", "Singapore", "contains")
     → "singapore" in "datacenter in singapore" → True ✓
   - Datacenter B: description = "Datacenter in Tokyo"
     → "singapore" in "datacenter in tokyo" → False ✗
   ↓
9. Tạo relationship: Datacenter A → Server
```

## 8. Performance Considerations

### Tối ưu cho EQUALS:
- Sử dụng database index với `value_table.get_by(attr_id=..., value=...)`
- Không cần scan tất cả CIs

### Các operator khác:
- Phải scan tất cả CIs của type tương ứng
- Có thể chậm nếu có nhiều CIs
- Nên cân nhắc khi có > 1000 CIs

### Best Practices:
1. Ưu tiên dùng `equals` khi có thể
2. Chỉ dùng `contains`, `in_list` khi thực sự cần
3. Đảm bảo có index trên attribute values

## 9. Error Handling

- Null values: Tự động return False
- Invalid operator: Fallback về equals
- JSON parse error: Log warning và tiếp tục
- Missing attributes: Skip và tiếp tục với attribute khác

## 10. Testing

Để test logic này:

```python
# Test _match_values
assert CIRelationManager._match_values("abc", "abc", "equals") == True
assert CIRelationManager._match_values("ABC", "abc", "contains") == True
assert CIRelationManager._match_values("a,b,c", "b,d", "in_list", separator=",") == True
assert CIRelationManager._match_values("b", "a,b,c", "has_one", separator=",") == True
assert CIRelationManager._match_values("2.5", "2.50", "compare") == True
```


