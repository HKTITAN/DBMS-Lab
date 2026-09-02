-- ============================================================
-- DBMS Lab · 26-08-2026
-- Employees table: CREATE, seed, then RENAME department → faculty
-- SQLite  (sql.js compiler / DB Browser / sqlite3)
-- For the class SQL Server, run employees.sqlserver.sql instead.
-- ============================================================

DROP TABLE IF EXISTS employees;

-- ------------------------------------------------------------
-- 1. Create the employees table
-- ------------------------------------------------------------
CREATE TABLE employees (
    empID      INTEGER PRIMARY KEY,
    empName    TEXT NOT NULL,
    department TEXT NOT NULL,
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
SELECT * FROM employees;
PRAGMA table_info(employees);

-- ------------------------------------------------------------
-- 4. Rename the column department → faculty
--    Row values are unchanged; only the column name changes.
-- ------------------------------------------------------------
ALTER TABLE employees RENAME COLUMN department TO faculty;

-- ------------------------------------------------------------
-- 5. Verify the table AFTER the rename
-- ------------------------------------------------------------
SELECT * FROM employees;
PRAGMA table_info(employees);
