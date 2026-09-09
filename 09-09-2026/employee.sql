-- ============================================================
-- DBMS Lab · 09-09-2026
-- Employee table: CREATE, seed 10 rows, then SELECT queries
-- DISTINCT, WHERE, BETWEEN, IN, ORDER BY
-- SQLite  (sql.js compiler / DB Browser / sqlite3)
-- For the class SQL Server, run employee.sqlserver.sql instead.
-- ============================================================

DROP TABLE IF EXISTS employee;

-- ------------------------------------------------------------
-- 1. Create the employee table
-- ------------------------------------------------------------
CREATE TABLE employee (
    sr_no          INTEGER PRIMARY KEY,
    employee_name  TEXT NOT NULL,
    job            TEXT NOT NULL,
    manager        TEXT,
    hire_date      DATE NOT NULL,
    salary         NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    department_no  INTEGER NOT NULL,
    city           TEXT NOT NULL
);

-- ------------------------------------------------------------
-- 2. Insert 10 sample rows
--    • salaries below, inside, and above 30000–50000
--    • cities: Delhi, Mumbai, Chennai, Bangalore, Hyderabad, Pune
--    • mixed department numbers (some duplicates)
--    • Rajesh Kumar is the top manager (manager IS NULL)
-- ------------------------------------------------------------
INSERT INTO employee
    (sr_no, employee_name, job, manager, hire_date, salary, department_no, city)
VALUES
    (1,  'Rajesh Kumar',    'General Manager',    NULL,            '2018-03-12', 85000.00, 10, 'Delhi'),
    (2,  'Ananya Sharma',   'Software Engineer',  'Rajesh Kumar',  '2021-07-01', 45000.00, 20, 'Bangalore'),
    (3,  'Rohan Mehta',     'Accountant',         'Rajesh Kumar',  '2020-01-15', 28000.00, 30, 'Mumbai'),
    (4,  'Priya Nair',      'HR Executive',       'Rajesh Kumar',  '2022-04-20', 32000.00, 40, 'Chennai'),
    (5,  'Vikram Singh',    'Sales Manager',      'Rajesh Kumar',  '2019-11-08', 52000.00, 50, 'Hyderabad'),
    (6,  'Fatima Khan',     'Software Engineer',  'Ananya Sharma', '2023-02-14', 38000.00, 20, 'Bangalore'),
    (7,  'Arjun Patel',     'Clerk',              'Rohan Mehta',   '2024-06-01', 18000.00, 30, 'Pune'),
    (8,  'Neha Gupta',      'Marketing Analyst',  'Rajesh Kumar',  '2021-09-10', 35000.00, 60, 'Delhi'),
    (9,  'Karan Iyer',      'Database Admin',     'Ananya Sharma', '2020-12-05', 48000.00, 20, 'Mumbai'),
    (10, 'Meera Joshi',     'Receptionist',       'Priya Nair',    '2023-08-22', 22000.00, 40, 'Chennai');

-- ------------------------------------------------------------
-- 3. Select all details from employee
-- ------------------------------------------------------------
-- All employee rows
SELECT * FROM employee;

-- ------------------------------------------------------------
-- 4. Select only DISTINCT department numbers
-- ------------------------------------------------------------
-- Distinct department numbers
SELECT DISTINCT department_no FROM employee;

-- ------------------------------------------------------------
-- 5. Select all department numbers (no DISTINCT)
-- ------------------------------------------------------------
-- All department numbers
SELECT department_no FROM employee;

-- ------------------------------------------------------------
-- 6. Employee name and salary where salary > 30000
-- ------------------------------------------------------------
-- Salary greater than 30000
SELECT employee_name, salary
FROM employee
WHERE salary > 30000;

-- ------------------------------------------------------------
-- 7. Employee name and hire date where city is NOT Delhi
-- ------------------------------------------------------------
-- City is not Delhi
SELECT employee_name, hire_date
FROM employee
WHERE city <> 'Delhi';

-- ------------------------------------------------------------
-- 8. Employee name and hire date where city is Delhi OR Mumbai
-- ------------------------------------------------------------
-- City is Delhi or Mumbai
SELECT employee_name, hire_date
FROM employee
WHERE city = 'Delhi' OR city = 'Mumbai';

-- ------------------------------------------------------------
-- 9. Employee number and name where salary BETWEEN 30000 AND 50000
-- ------------------------------------------------------------
-- Salary between 30000 and 50000
SELECT sr_no, employee_name
FROM employee
WHERE salary BETWEEN 30000 AND 50000;

-- ------------------------------------------------------------
-- 10. Employee number and name where salary NOT BETWEEN 30000 AND 50000
-- ------------------------------------------------------------
-- Salary not between 30000 and 50000
SELECT sr_no, employee_name
FROM employee
WHERE salary NOT BETWEEN 30000 AND 50000;

-- ------------------------------------------------------------
-- 11. All details where city IN (Delhi, Mumbai, Chennai, Bangalore)
-- ------------------------------------------------------------
-- City in metro list
SELECT *
FROM employee
WHERE city IN ('Delhi', 'Mumbai', 'Chennai', 'Bangalore');

-- ------------------------------------------------------------
-- 12. All details where city NOT IN (Mumbai, Delhi, Chennai)
-- ------------------------------------------------------------
-- City not in Mumbai, Delhi, Chennai
SELECT *
FROM employee
WHERE city NOT IN ('Mumbai', 'Delhi', 'Chennai');

-- ------------------------------------------------------------
-- 13. All details ordered by employee name DESC
-- ------------------------------------------------------------
-- Employees in descending name order
SELECT *
FROM employee
ORDER BY employee_name DESC;

-- ------------------------------------------------------------
-- 14. All details ordered by employee name ASC
-- ------------------------------------------------------------
-- Employees in ascending name order
SELECT *
FROM employee
ORDER BY employee_name ASC;
