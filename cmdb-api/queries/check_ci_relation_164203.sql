-- ============================================
-- Queries để kiểm tra CI Relation cho CI ID 164203
-- ============================================

-- 1. Kiểm tra CI 164203 có tồn tại không và type_id của nó
SELECT 
    id,
    type_id,
    status,
    heartbeat,
    is_auto_discovery,
    updated_by,
    created_at,
    updated_at
FROM c_cis
WHERE id = 164203
AND deleted = 0;

-- 2. Lấy tên CI Type của CI 164203
SELECT 
    ci.id AS ci_id,
    ci.type_id,
    ct.name AS type_name,
    ct.alias AS type_alias
FROM c_cis ci
LEFT JOIN c_ci_types ct ON ci.type_id = ct.id
WHERE ci.id = 164203
AND ci.deleted = 0;

-- 3. Tìm PARENTS của CI 164203 (CI 164203 là child/second_ci)
-- Đây là các CI mà 164203 phụ thuộc vào (từ con lên cha)
SELECT 
    cr.id AS relation_id,
    cr.first_ci_id AS parent_ci_id,
    cr.second_ci_id AS child_ci_id,
    cr.relation_type_id,
    rt.name AS relation_type_name,
    parent_ci.type_id AS parent_type_id,
    parent_ct.name AS parent_type_name,
    child_ci.type_id AS child_type_id,
    child_ct.name AS child_type_name,
    cr.ancestor_ids,
    cr.deleted AS relation_deleted,
    cr.created_at,
    cr.updated_at
FROM c_ci_relations cr
LEFT JOIN c_cis parent_ci ON cr.first_ci_id = parent_ci.id
LEFT JOIN c_cis child_ci ON cr.second_ci_id = child_ci.id
LEFT JOIN c_ci_types parent_ct ON parent_ci.type_id = parent_ct.id
LEFT JOIN c_ci_types child_ct ON child_ci.type_id = child_ct.id
LEFT JOIN c_relation_types rt ON cr.relation_type_id = rt.id
WHERE cr.second_ci_id = 164203  -- CI 164203 là child
AND cr.deleted = 0
ORDER BY cr.created_at DESC;

-- 4. Tìm CHILDREN của CI 164203 (CI 164203 là parent/first_ci)
-- Đây là các CI mà 164203 có quan hệ với (từ cha xuống con)
SELECT 
    cr.id AS relation_id,
    cr.first_ci_id AS parent_ci_id,
    cr.second_ci_id AS child_ci_id,
    cr.relation_type_id,
    rt.name AS relation_type_name,
    parent_ci.type_id AS parent_type_id,
    parent_ct.name AS parent_type_name,
    child_ci.type_id AS child_type_id,
    child_ct.name AS child_type_name,
    cr.ancestor_ids,
    cr.deleted AS relation_deleted,
    cr.created_at,
    cr.updated_at
FROM c_ci_relations cr
LEFT JOIN c_cis parent_ci ON cr.first_ci_id = parent_ci.id
LEFT JOIN c_cis child_ci ON cr.second_ci_id = child_ci.id
LEFT JOIN c_ci_types parent_ct ON parent_ci.type_id = parent_ct.id
LEFT JOIN c_ci_types child_ct ON child_ci.type_id = child_ct.id
LEFT JOIN c_relation_types rt ON cr.relation_type_id = rt.id
WHERE cr.first_ci_id = 164203  -- CI 164203 là parent
AND cr.deleted = 0
ORDER BY cr.created_at DESC;

-- 5. Kiểm tra CITypeRelation được định nghĩa cho type của CI 164203
-- Tìm các quan hệ type mà type của CI 164203 có thể là child (có thể có parents)
SELECT 
    ctr.id AS type_relation_id,
    ctr.parent_id AS parent_type_id,
    parent_ct.name AS parent_type_name,
    ctr.child_id AS child_type_id,
    child_ct.name AS child_type_name,
    ctr.relation_type_id,
    rt.name AS relation_type_name,
    ctr.constraint,
    ctr.deleted AS type_relation_deleted
FROM c_ci_type_relations ctr
LEFT JOIN c_ci_types parent_ct ON ctr.parent_id = parent_ct.id
LEFT JOIN c_ci_types child_ct ON ctr.child_id = child_ct.id
LEFT JOIN c_relation_types rt ON ctr.relation_type_id = rt.id
WHERE ctr.child_id = (
    SELECT type_id FROM c_cis WHERE id = 164203 AND deleted = 0
)  -- Type của CI 164203 có thể là child
AND ctr.deleted = 0
ORDER BY ctr.created_at DESC;

-- 6. Kiểm tra CITypeRelation mà type của CI 164203 có thể là parent (có thể có children)
SELECT 
    ctr.id AS type_relation_id,
    ctr.parent_id AS parent_type_id,
    parent_ct.name AS parent_type_name,
    ctr.child_id AS child_type_id,
    child_ct.name AS child_type_name,
    ctr.relation_type_id,
    rt.name AS relation_type_name,
    ctr.constraint,
    ctr.deleted AS type_relation_deleted
FROM c_ci_type_relations ctr
LEFT JOIN c_ci_types parent_ct ON ctr.parent_id = parent_ct.id
LEFT JOIN c_ci_types child_ct ON ctr.child_id = child_ct.id
LEFT JOIN c_relation_types rt ON ctr.relation_type_id = rt.id
WHERE ctr.parent_id = (
    SELECT type_id FROM c_cis WHERE id = 164203 AND deleted = 0
)  -- Type của CI 164203 có thể là parent
AND ctr.deleted = 0
ORDER BY ctr.created_at DESC;

-- 7. Kiểm tra ancestor_ids có được populate không
-- Nếu ancestor_ids NULL hoặc rỗng, có thể là nguyên nhân của vấn đề
SELECT 
    COUNT(*) AS total_relations,
    COUNT(ancestor_ids) AS relations_with_ancestor_ids,
    COUNT(*) - COUNT(ancestor_ids) AS relations_without_ancestor_ids,
    COUNT(CASE WHEN second_ci_id = 164203 THEN 1 END) AS relations_for_ci_164203_as_child,
    COUNT(CASE WHEN second_ci_id = 164203 AND ancestor_ids IS NOT NULL THEN 1 END) AS relations_with_ancestor_for_ci_164203
FROM c_ci_relations
WHERE deleted = 0;

-- 8. Tổng hợp: Tất cả quan hệ liên quan đến CI 164203
SELECT 
    'PARENT' AS relation_direction,
    cr.first_ci_id AS related_ci_id,
    ct.name AS related_ci_type,
    rt.name AS relation_type_name,
    cr.ancestor_ids,
    cr.created_at
FROM c_ci_relations cr
LEFT JOIN c_cis ci ON cr.first_ci_id = ci.id
LEFT JOIN c_ci_types ct ON ci.type_id = ct.id
LEFT JOIN c_relation_types rt ON cr.relation_type_id = rt.id
WHERE cr.second_ci_id = 164203
AND cr.deleted = 0

UNION ALL

SELECT 
    'CHILD' AS relation_direction,
    cr.second_ci_id AS related_ci_id,
    ct.name AS related_ci_type,
    rt.name AS relation_type_name,
    cr.ancestor_ids,
    cr.created_at
FROM c_ci_relations cr
LEFT JOIN c_cis ci ON cr.second_ci_id = ci.id
LEFT JOIN c_ci_types ct ON ci.type_id = ct.id
LEFT JOIN c_relation_types rt ON cr.relation_type_id = rt.id
WHERE cr.first_ci_id = 164203
AND cr.deleted = 0

ORDER BY relation_direction, created_at DESC;

-- 9. Kiểm tra xem có CIRelation nào bị deleted không (có thể gây nhầm lẫn)
SELECT 
    COUNT(*) AS total_deleted_relations_for_164203
FROM c_ci_relations
WHERE (first_ci_id = 164203 OR second_ci_id = 164203)
AND deleted = 1;

-- 10. Kiểm tra Redis cache (nếu có) - cần chạy trong Redis CLI
-- KEYS cmdb:ci_relation:164203*
-- GET cmdb:ci_relation:164203

