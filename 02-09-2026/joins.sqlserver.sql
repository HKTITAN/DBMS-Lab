-- ============================================================
-- DBMS Lab · 02-09-2026
-- SQL Joins: CROSS, NATURAL, INNER, OUTER (LEFT/RIGHT), SELF
-- Microsoft SQL Server (T-SQL) — use this on the class server
-- ============================================================

DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- ------------------------------------------------------------
-- 1. Create related tables
--    • deptID links employees → departments
--    • managerID links employees → employees (for SELF JOIN)
-- ------------------------------------------------------------
CREATE TABLE departments (
    deptID   INT PRIMARY KEY,
    deptName VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    empID      INT PRIMARY KEY,
    empName    VARCHAR(100) NOT NULL,
    deptID     INT NOT NULL,
    managerID  INT NULL,
    salary     NUMERIC(10, 2) NOT NULL CHECK (salary > 0)
);

-- ------------------------------------------------------------
-- 2. Insert sample rows
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
SELECT * FROM departments;
SELECT * FROM employees;

-- ------------------------------------------------------------
-- 4. CROSS JOIN
-- ------------------------------------------------------------
SELECT COUNT(*) AS cross_join_row_count
FROM departments
CROSS JOIN employees;

SELECT TOP 8 d.deptName, e.empName
FROM departments AS d
CROSS JOIN employees AS e
ORDER BY d.deptID, e.empID;

-- ------------------------------------------------------------
-- 5. NATURAL JOIN — not supported in SQL Server; equivalent:
-- ------------------------------------------------------------
SELECT e.empID, e.empName, d.deptName, e.salary
FROM employees AS e
INNER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 6. INNER JOIN
-- ------------------------------------------------------------
SELECT e.empID, e.empName, d.deptName, e.salary
FROM employees AS e
INNER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 7a. LEFT OUTER JOIN
-- ------------------------------------------------------------
SELECT e.empID, e.empName, e.deptID, d.deptName, e.salary
FROM employees AS e
LEFT OUTER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 7b. RIGHT OUTER JOIN
-- ------------------------------------------------------------
SELECT e.empID, e.empName, d.deptID, d.deptName, e.salary
FROM employees AS e
RIGHT OUTER JOIN departments AS d ON e.deptID = d.deptID;

-- ------------------------------------------------------------
-- 8. SELF JOIN
-- ------------------------------------------------------------
SELECT
    e.empName  AS employee,
    m.empName  AS manager
FROM employees AS e
LEFT JOIN employees AS m ON e.managerID = m.empID
ORDER BY e.empID;
