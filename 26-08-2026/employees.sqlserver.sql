-- ============================================================
-- DBMS Lab · 26-08-2026
-- Employees table: CREATE, seed, then RENAME department → faculty
-- Microsoft SQL Server (T-SQL) — use this on the class server
-- ============================================================

DROP TABLE IF EXISTS employees;

-- ------------------------------------------------------------
-- 1. Create the employees table
-- ------------------------------------------------------------
CREATE TABLE employees (
    empID      INT PRIMARY KEY,
    empName    VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    salary     NUMERIC(10, 2) NOT NULL CHECK (salary > 0)
);

-- ------------------------------------------------------------
-- 2. Insert sample rows (department holds the faculty/school name)
-- ------------------------------------------------------------
INSERT INTO employees (empID, empName, department, salary) VALUES
    (1, 'Ananya Sharma',  'School of Engineering and Technology', 92000.00),
    (2, 'Rohan Mehta',    'School of Management',                 78000.00),
    (3, 'Priya Nair',     'School of Law',                        85000.00),
    (4, 'Vikram Singh',   'School of Agricultural Sciences',      76000.00),
    (5, 'Fatima Khan',    'School of Engineering and Technology', 88000.00),
    (6, 'Arjun Patel',    'School of Medical Sciences',           95000.00);

-- ------------------------------------------------------------
-- 3. Verify the table BEFORE the rename
-- ------------------------------------------------------------
-- Employees before column rename
SELECT * FROM employees;

-- Table columns before rename
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'employees'
ORDER BY ORDINAL_POSITION;

-- ------------------------------------------------------------
-- 4. Rename the column department → faculty
--    SQL Server does not support ALTER TABLE ... RENAME COLUMN.
--    Use sp_rename. Row values are unchanged; only the name changes.
-- ------------------------------------------------------------
EXEC sp_rename 'employees.department', 'faculty', 'COLUMN';

-- ------------------------------------------------------------
-- 5. Verify the table AFTER the rename
-- ------------------------------------------------------------
-- Employees after column rename
SELECT * FROM employees;

-- Table columns after rename
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'employees'
ORDER BY ORDINAL_POSITION;
