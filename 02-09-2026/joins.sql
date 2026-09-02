-- ============================================================
-- DBMS Lab · 02-09-2026
-- SQL Joins: CROSS, NATURAL, INNER, OUTER (LEFT/RIGHT), SELF
-- SQLite  (sql.js compiler / DB Browser / sqlite3)
-- For the class SQL Server, run joins.sqlserver.sql instead.
-- ============================================================

DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- ------------------------------------------------------------
-- 1. Create related tables
--    • deptID links employees → departments
--    • managerID links employees → employees (for SELF JOIN)
-- ------------------------------------------------------------
CREATE TABLE departments (
    deptID   INTEGER PRIMARY KEY,
    deptName TEXT NOT NULL
);

CREATE TABLE employees (
    empID      INTEGER PRIMARY KEY,
    empName    TEXT NOT NULL,
    deptID     INTEGER NOT NULL,
    managerID  INTEGER,
    salary     NUMERIC(10, 2) NOT NULL CHECK (salary > 0)
);

-- ------------------------------------------------------------
-- 2. Insert sample rows
--    • deptID 6 (Humanities) has no employees  → RIGHT OUTER JOIN
--    • empID 7 points to deptID 99 (missing)   → LEFT OUTER JOIN
--    • managerID links form a simple reporting chain → SELF JOIN
-- ------------------------------------------------------------
INSERT INTO departments (deptID, deptName) VALUES
    (1, 'School of Engineering and Technology'),
    (2, 'School of Management'),
    (3, 'School of Law'),
    (4, 'School of Agricultural Sciences'),
    (5, 'School of Medical Sciences'),
    (6, 'School of Humanities');

INSERT INTO employees (empID, empName, deptID, managerID, salary) VALUES
    (1, 'Ananya Sharma', 1, NULL,  92000.00),
    (2, 'Rohan Mehta',   2, 1,     78000.00),
    (3, 'Priya Nair',    3, 1,     85000.00),
    (4, 'Vikram Singh',  4, 2,     76000.00),
    (5, 'Fatima Khan',   1, 1,     88000.00),
    (6, 'Arjun Patel',   5, 3,     95000.00),
    (7, 'Neha Gupta',   99, 2,     54000.00);

-- ------------------------------------------------------------
-- 3. Base tables (reference)
-- ------------------------------------------------------------
-- List all departments
SELECT * FROM departments;
-- List all employees
SELECT * FROM employees;

-- ------------------------------------------------------------
-- 4. CROSS JOIN
--    Cartesian product: every row of table A paired with every
--    row of table B. No join condition. Here: 6 × 7 = 42 rows.
-- ------------------------------------------------------------
-- Count cross join rows
SELECT COUNT(*) AS cross_join_row_count
FROM departments
CROSS JOIN employees;

-- Cross join sample pairs
SELECT d.deptName, e.empName
FROM departments AS d
CROSS JOIN employees AS e
ORDER BY d.deptID, e.empID
LIMIT 8;

-- ------------------------------------------------------------
-- 5. NATURAL JOIN
--    Matches on every column with the same name (here: deptID).
--    Only rows with a matching deptID in BOTH tables appear.
-- ------------------------------------------------------------
-- Natural join on deptID
SELECT empID, empName, deptName, salary
FROM employees
NATURAL JOIN departments;

-- ------------------------------------------------------------
-- 6. INNER JOIN
--    Explicit join condition; same result as NATURAL JOIN here
--    because deptID is the only common column.
-- ------------------------------------------------------------
-- Inner join employees and departments
SELECT e.empID, e.empName, d.deptName, e.salary
FROM employees AS e
INNER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 7a. LEFT OUTER JOIN
--     All rows from the LEFT table (employees); unmatched dept
--     columns are NULL (empID 7 → deptID 99 has no department).
-- ------------------------------------------------------------
-- Left join — keep all employees
SELECT e.empID, e.empName, e.deptID, d.deptName, e.salary
FROM employees AS e
LEFT OUTER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 7b. RIGHT OUTER JOIN
--     All rows from the RIGHT table (departments); unmatched
--     employee columns are NULL (deptID 6 has no employees).
--     Requires SQLite 3.39+; see joins.sqlserver.sql for T-SQL.
-- ------------------------------------------------------------
-- Right join — keep all departments
SELECT e.empID, e.empName, d.deptID, d.deptName, e.salary
FROM employees AS e
RIGHT OUTER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 8. SELF JOIN
--     A table joined to itself using different aliases.
--     Here: each employee matched to their manager (also in
--     employees). Ananya has no manager → manager name is NULL.
-- ------------------------------------------------------------
-- Self join — employee to manager
SELECT
    e.empName  AS employee,
    m.empName  AS manager
FROM employees AS e
LEFT JOIN employees AS m ON e.managerID = m.empID
ORDER BY e.empID;
