-- Migration: Add matching_rules field to c_ci_type_relations table
-- This field stores advanced matching rules for attribute-based relationship creation
-- Format: JSON array of objects with parent_attr_id, child_attr_id, operator, and optional separator

ALTER TABLE `c_ci_type_relations` 
ADD COLUMN `matching_rules` JSON NULL COMMENT 'Advanced matching rules for attribute-based relationships';

-- Example matching_rules format:
-- [
--   {
--     "parent_attr_id": 1,
--     "child_attr_id": 2,
--     "operator": "contains",
--     "separator": ","
--   },
--   {
--     "parent_attr_id": 3,
--     "child_attr_id": 4,
--     "operator": "in_list",
--     "separator": "|"
--   },
--   {
--     "parent_attr_id": 5,
--     "child_attr_id": 6,
--     "operator": "in_list",
--     "parent_separator": "|",
--     "child_separator": ","
--   }
-- ]
--
-- Supported operators:
-- - "equals": Exact match (default)
-- - "contains": Parent contains child string
-- - "in_list": Both are lists, check intersection
-- - "has_one": Parent has one of child values
-- - "compare": Numeric comparison
--
-- Separator fields:
-- - "separator": Common separator for both parent and child (default: ",")
-- - "parent_separator": Separator for parent value only (optional)
-- - "child_separator": Separator for child value only (optional)
-- If parent_separator or child_separator is specified, it takes precedence over separator

