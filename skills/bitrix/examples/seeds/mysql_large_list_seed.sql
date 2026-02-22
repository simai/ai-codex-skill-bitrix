-- MySQL 8+ large dataset for admin list/filter/pagination checks.
-- Creates 100000 rows in qa_employees_perf.

CREATE TABLE IF NOT EXISTS qa_employees_perf (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ext_code VARCHAR(32) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(32) NOT NULL,
  department VARCHAR(120) NOT NULL,
  position_name VARCHAR(120) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  sort INT NOT NULL DEFAULT 500,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY ux_qa_employees_perf_ext_code (ext_code),
  KEY ix_qa_employees_perf_department (department),
  KEY ix_qa_employees_perf_active (is_active),
  KEY ix_qa_employees_perf_sort (sort),
  KEY ix_qa_employees_perf_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Safe rerun mode: replace table content.
TRUNCATE TABLE qa_employees_perf;

SET @seed_size := 100000;

WITH digits AS (
  SELECT 0 AS d UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
  UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
),
seq AS (
  SELECT
    (d1.d + d2.d * 10 + d3.d * 100 + d4.d * 1000 + d5.d * 10000) + 1 AS n
  FROM digits d1
  CROSS JOIN digits d2
  CROSS JOIN digits d3
  CROSS JOIN digits d4
  CROSS JOIN digits d5
)
INSERT INTO qa_employees_perf (
  ext_code,
  full_name,
  email,
  phone,
  department,
  position_name,
  is_active,
  sort,
  created_at
)
SELECT
  CONCAT('EMP-', LPAD(n, 6, '0')),
  CONCAT('Employee ', LPAD(n, 6, '0')),
  CONCAT('employee', n, '@example.test'),
  CONCAT('+1-555-', LPAD(n % 10000, 4, '0')),
  ELT((n % 8) + 1, 'Sales', 'Support', 'IT', 'HR', 'Finance', 'Ops', 'Legal', 'Marketing'),
  ELT((n % 6) + 1, 'Specialist', 'Senior Specialist', 'Manager', 'Lead', 'Analyst', 'Director'),
  IF(n % 10 = 0, 0, 1),
  (n % 1000) + 10,
  TIMESTAMPADD(MINUTE, -n, NOW())
FROM seq
WHERE n <= @seed_size;

SELECT COUNT(*) AS inserted_rows FROM qa_employees_perf;
