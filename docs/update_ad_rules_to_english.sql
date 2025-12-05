-- Update Auto Discovery Rules from Chinese to English
-- This script updates the c_ad_rules table to use English names

-- Update Cloud Providers
UPDATE c_ad_rules SET name = 'Aliyun' WHERE name = '阿里云' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Tencent Cloud' WHERE name = '腾讯云' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Huawei Cloud' WHERE name = '华为云' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'AWS' WHERE name = 'AWS' AND is_inner = 1;

-- Update Virtualization
UPDATE c_ad_rules SET name = 'VCenter' WHERE name = 'VCenter' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'KVM' WHERE name = 'KVM' AND is_inner = 1;

-- Update Web Servers
UPDATE c_ad_rules SET name = 'Nginx' WHERE name = 'Nginx' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Apache' WHERE name = 'Apache' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Tomcat' WHERE name = 'Tomcat' AND is_inner = 1;

-- Update Databases
UPDATE c_ad_rules SET name = 'MySQL' WHERE name = 'MySQL' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'MSSQL' WHERE name = 'MSSQL' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Oracle' WHERE name = 'Oracle' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Redis' WHERE name = 'Redis' AND is_inner = 1;

-- Update Network Devices
UPDATE c_ad_rules SET name = 'Switch' WHERE name = '交换机' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Router' WHERE name = '路由器' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Firewall' WHERE name = '防火墙' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'Fiber Channel Switch' WHERE name = '光纤交换机' AND is_inner = 1;
UPDATE c_ad_rules SET name = 'F5' WHERE name = 'F5' AND is_inner = 1;

-- Update CI Type Groups (if stored in c_ad_rules)
-- Note: These might be in ci_type_groups table instead
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"云资源"', '"category":"Cloud"') WHERE option LIKE '%"分类":"云资源"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"虚拟化"', '"category":"Virtualization"') WHERE option LIKE '%"分类":"虚拟化"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"中间件"', '"category":"Middleware"') WHERE option LIKE '%"分类":"中间件"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"数据库"', '"category":"Database"') WHERE option LIKE '%"分类":"数据库"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"网络设备"', '"category":"Network Device"') WHERE option LIKE '%"分类":"网络设备"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"分类":"负载均衡"', '"category":"Load Balancer"') WHERE option LIKE '%"分类":"负载均衡"%';

-- Update category values if stored directly
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"云资源"', '"category":"Cloud"') WHERE option LIKE '%"category":"云资源"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"虚拟化"', '"category":"Virtualization"') WHERE option LIKE '%"category":"虚拟化"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"中间件"', '"category":"Middleware"') WHERE option LIKE '%"category":"中间件"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"数据库"', '"category":"Database"') WHERE option LIKE '%"category":"数据库"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"网络设备"', '"category":"Network Device"') WHERE option LIKE '%"category":"网络设备"%';
UPDATE c_ad_rules SET option = REPLACE(option, '"category":"负载均衡"', '"category":"Load Balancer"') WHERE option LIKE '%"category":"负载均衡"%';

-- Update CI Type Group names in ci_type_groups table
UPDATE ci_type_groups SET name = 'Compute' WHERE name = '计算' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Network' WHERE name = '网络' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Storage' WHERE name = '存储' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Database' WHERE name = '数据库' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Middleware' WHERE name = '中间件' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Security' WHERE name = '安全' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Monitor' WHERE name = '监控' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Cloud' WHERE name = '云资源' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Virtualization' WHERE name = '虚拟化' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Network Device' WHERE name = '网络设备' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Load Balancer' WHERE name = '负载均衡' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Container' WHERE name = '容器' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Application' WHERE name = '应用' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);
UPDATE ci_type_groups SET name = 'Other' WHERE name = '其他' AND type_id IN (SELECT id FROM ci_types WHERE is_inner = 1);

-- Verify the changes
SELECT 
    id,
    name,
    option,
    is_inner,
    created_at
FROM c_ad_rules
WHERE is_inner = 1
ORDER BY name;

-- Verify CI Type Group changes
SELECT 
    id,
    name,
    type_id
FROM ci_type_groups
ORDER BY name;


