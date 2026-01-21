-- Migration: Add description and impact fields to c_relation_types table
-- This migration adds:
-- 1. description: Text field to describe what this connection is
-- 2. first_ci_to_second_ci_impact: Impact from first_ci to second_ci (0=None, 2=Low, 5=Medium, 7=High, 10=Critical)
-- 3. second_ci_to_first_ci_impact: Impact from second_ci back to first_ci (same scale)
--
-- Usage: Run this script to add the new columns to c_relation_types table
-- Rollback: See rollback section at the bottom of this file

-- Check if columns don't exist before adding (safe to run multiple times)
SET @dbname = DATABASE();
SET @tablename = 'c_relation_types';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'description'
    ) = 0,
    'ALTER TABLE `c_relation_types` ADD COLUMN `description` TEXT NULL COMMENT ''Mô tả kết nối này là gì'';',
    'SELECT "Column description already exists, skipping...";'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'first_ci_to_second_ci_impact'
    ) = 0,
    'ALTER TABLE `c_relation_types` ADD COLUMN `first_ci_to_second_ci_impact` INT NOT NULL DEFAULT 0 COMMENT ''Ảnh hưởng từ first_ci đến second_ci (0=None, 2=Low, 5=Medium, 7=High, 10=Critical)'';',
    'SELECT "Column first_ci_to_second_ci_impact already exists, skipping...";'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = @dbname
        AND TABLE_NAME = @tablename
        AND COLUMN_NAME = 'second_ci_to_first_ci_impact'
    ) = 0,
    'ALTER TABLE `c_relation_types` ADD COLUMN `second_ci_to_first_ci_impact` INT NOT NULL DEFAULT 0 COMMENT ''Ảnh hưởng từ second_ci ngược lại first_ci (0=None, 2=Low, 5=Medium, 7=High, 10=Critical)'';',
    'SELECT "Column second_ci_to_first_ci_impact already exists, skipping...";'
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Impact scale:
-- 0 = None (Không có ảnh hưởng)
-- 2 = Low (Ảnh hưởng thấp)
-- 5 = Medium (Ảnh hưởng trung bình)
-- 7 = High (Ảnh hưởng cao)
-- 10 = Critical (Ảnh hưởng nghiêm trọng)

-- ============================================
-- ROLLBACK SCRIPT (Run this to undo migration)
-- ============================================
-- ALTER TABLE `c_relation_types` 
-- DROP COLUMN IF EXISTS `description`,
-- DROP COLUMN IF EXISTS `first_ci_to_second_ci_impact`,
-- DROP COLUMN IF EXISTS `second_ci_to_first_ci_impact`;

