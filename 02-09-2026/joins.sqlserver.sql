-- ============================================================
-- DBMS Lab · 02-09-2026
-- SQL Joins: NATURAL, INNER, LEFT OUTER, RIGHT OUTER
-- Microsoft SQL Server (T-SQL) — use this on the class server
-- ============================================================

DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- ------------------------------------------------------------
-- 1. Create related tables (common column: deptID)
-- ------------------------------------------------------------
CREATE TABLE departments (
    deptID   INT PRIMARY KEY,
    deptName VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    empID    INT PRIMARY KEY,
    empName  VARCHAR(100) NOT NULL,
    deptID   INT NOT NULL,
    salary   NUMERIC(10, 2) NOT NULL CHECK (salary > 0)
);

-- ------------------------------------------------------------
-- 2. Insert sample rows
--    • deptID 6 (Humanities) has no employees  → visible in RIGHT OUTER JOIN
--    • empID 7 points to deptID 99 (missing) → visible in LEFT OUTER JOIN
-- ------------------------------------------------------------
INSERT INTO departments (deptID, deptName) VALUES
    (1, 'School of Engineering and Technology'),
    (2, 'School of Management'),
    (3, 'School of Law'),
    (4, 'School of Agricultural Sciences'),
    (5, 'School of Medical Sciences'),
    (6, 'School of Humanities');

INSERT INTO employees (empID, empName, deptID, salary) VALUES
    (1, 'Ananya Sharma', 1, 92000.00),
    (2, 'Rohan Mehta',   2, 78000.00),
    (3, 'Priya Nair',    3, 85000.00),
    (4, 'Vikram Singh',  4, 76000.00),
    (5, 'Fatima Khan',   1, 88000.00),
    (6, 'Arjun Patel',   5, 95000.00),
    (7, 'Neha Gupta',   99, 54000.00);

-- ------------------------------------------------------------
-- 3. Base tables (reference)
-- ------------------------------------------------------------
SELECT * FROM departments;
SELECT * FROM employees;

-- ------------------------------------------------------------
-- 4. NATURAL JOIN
--    Matches rows on every column with the same name (here: deptID).
--    Only rows with a matching deptID in BOTH tables appear.
-- ------------------------------------------------------------
SELECT empID, empName, deptName, salary
FROM employees
NATURAL JOIN departments;

-- ------------------------------------------------------------
-- 5. INNER JOIN
--    Explicit join condition; same result as NATURAL JOIN here
--    because deptID is the only common column.
-- ------------------------------------------------------------
SELECT e.empID, e.empName, d.deptName, e.salary
FROM employees AS e
INNER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 6a. LEFT OUTER JOIN
--     All rows from the LEFT table (employees); unmatched dept
--     columns are NULL (empID 7 → deptID 99 has no department).
-- ------------------------------------------------------------
SELECT e.empID, e.empName, e.deptID, d.deptName, e.salary
FROM employees AS e
LEFT OUTER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 6b. RIGHT OUTER JOIN
--     All rows from the RIGHT table (departments); unmatched
--     employee columns are NULL (deptID 6 has no employees).
-- ------------------------------------------------------------
SELECT e.empID, e.empName, d.deptID, d.deptName, e.salary
FROM employees AS e
RIGHT OUTER JOIN departments AS d ON e.deptID = d.deptID;
