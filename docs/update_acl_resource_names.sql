-- Update ACL Resource Type names from Chinese to English
-- This script updates the resource type and resource names in the ACL system

-- Update Resource Type name
UPDATE acl_resource_types 
SET name = 'Operation Permission'
WHERE name = '操作权限' AND app_id IN (SELECT id FROM acl_apps WHERE name = 'backend');

-- Update Resource names
UPDATE acl_resources 
SET name = 'Company Info'
WHERE name = '公司信息' 
AND resource_type_id IN (
    SELECT id FROM acl_resource_types 
    WHERE name = 'Operation Permission' 
    AND app_id IN (SELECT id FROM acl_apps WHERE name = 'backend')
);

UPDATE acl_resources 
SET name = 'Company Structure'
WHERE name = '公司架构' 
AND resource_type_id IN (
    SELECT id FROM acl_resource_types 
    WHERE name = 'Operation Permission' 
    AND app_id IN (SELECT id FROM acl_apps WHERE name = 'backend')
);

UPDATE acl_resources 
SET name = 'Notice Settings'
WHERE name = '通知设置' 
AND resource_type_id IN (
    SELECT id FROM acl_resource_types 
    WHERE name = 'Operation Permission' 
    AND app_id IN (SELECT id FROM acl_apps WHERE name = 'backend')
);

-- Verify the changes
SELECT 
    rt.name as resource_type_name,
    r.name as resource_name,
    r.id as resource_id
FROM acl_resources r
JOIN acl_resource_types rt ON r.resource_type_id = rt.id
JOIN acl_apps a ON rt.app_id = a.id
WHERE a.name = 'backend' 
AND rt.name = 'Operation Permission'
ORDER BY r.name;

