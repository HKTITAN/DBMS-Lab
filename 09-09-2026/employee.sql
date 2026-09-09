-- ============================================================
-- DBMS Lab · 09-09-2026
-- Employee table: CREATE, seed 10 rows, then SELECT queries
-- DISTINCT, WHERE, BETWEEN, IN, ORDER BY
-- SQLite  (sql.js compiler / DB Browser / sqlite3)
-- For the class SQL Server, run employee.sqlserver.sql instead.
--
-- Lab questions (wording as given; "distant" = DISTINCT)
-- 1. create a table employee with the following attributes:
--    sr no, employee name, job, manager, hire date, salary,
--    department no, city
-- 1. insert 10 rows in the above mentioned table
-- 2. select all the details from the employee table
-- 3. select only distant department number from employee table
-- 4. select all department numbers from employee table
-- 5. select employee name, salary where salary is >30000 rs
--    from employee table
-- 6. select employee name, hire date where city is not delhi
--    from employee table
-- 7. select employee name, hire date where city is either
--    delhi or mumbai from employee table
-- 8. select employee number, employee name where salary is
--    between 30000 rs and 50000 rs
-- 9. select employee number, employee name where salary is
--    not between 30000 and 50000 from employee table
-- 10. select all the details where city is among the following:
--     delhi, mumbai, chennai, Bangalore
-- 11. select all the details where city is not mumbai, delhi
--     or chennai from employee table
-- 12. select all the details from the employee table and
--     order by employee names in descending order.
-- 13. display the list of employees in ascending order from
--     employee table.
-- ============================================================

DROP TABLE IF EXISTS employee;

-- ------------------------------------------------------------
-- 1. create a table employee with the following attributes:
--    sr no, employee name, job, manager, hire date, salary,
--    department no, city
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
-- 1. insert 10 rows in the above mentioned table
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
-- 2. select all the details from the employee table
-- ------------------------------------------------------------
-- All the details from employee
SELECT * FROM employee;

-- ------------------------------------------------------------
-- 3. select only distant department number from employee table
--    ("distant" on the lab sheet = DISTINCT)
-- ------------------------------------------------------------
-- Distant (DISTINCT) department number
SELECT DISTINCT department_no FROM employee;

-- ------------------------------------------------------------
-- 4. select all department numbers from employee table
-- ------------------------------------------------------------
-- All department numbers
SELECT department_no FROM employee;

-- ------------------------------------------------------------
-- 5. select employee name, salary where salary is >30000 rs
--    from employee table
-- ------------------------------------------------------------
-- Salary > 30000 rs
SELECT employee_name, salary
FROM employee
WHERE salary > 30000;

-- ------------------------------------------------------------
-- 6. select employee name, hire date where city is not delhi
--    from employee table
-- ------------------------------------------------------------
-- City is not delhi
SELECT employee_name, hire_date
FROM employee
WHERE city <> 'Delhi';

-- ------------------------------------------------------------
-- 7. select employee name, hire date where city is either
--    delhi or mumbai from employee table
-- ------------------------------------------------------------
-- City is either delhi or mumbai
SELECT employee_name, hire_date
FROM employee
WHERE city = 'Delhi' OR city = 'Mumbai';

-- ------------------------------------------------------------
-- 8. select employee number, employee name where salary is
--    between 30000 rs and 50000 rs
-- ------------------------------------------------------------
-- Salary between 30000 rs and 50000 rs
SELECT sr_no, employee_name
FROM employee
WHERE salary BETWEEN 30000 AND 50000;

-- ------------------------------------------------------------
-- 9. select employee number, employee name where salary is
--    not between 30000 and 50000 from employee table
-- ------------------------------------------------------------
-- Salary not between 30000 and 50000
SELECT sr_no, employee_name
FROM employee
WHERE salary NOT BETWEEN 30000 AND 50000;

-- ------------------------------------------------------------
-- 10. select all the details where city is among the following:
--     delhi, mumbai, chennai, Bangalore
-- ------------------------------------------------------------
-- City among delhi, mumbai, chennai, Bangalore
SELECT *
FROM employee
WHERE city IN ('Delhi', 'Mumbai', 'Chennai', 'Bangalore');

-- ------------------------------------------------------------
-- 11. select all the details where city is not mumbai, delhi
--     or chennai from employee table
-- ------------------------------------------------------------
-- City is not mumbai, delhi or chennai
SELECT *
FROM employee
WHERE city NOT IN ('Mumbai', 'Delhi', 'Chennai');

-- ------------------------------------------------------------
-- 12. select all the details from the employee table and
--     order by employee names in descending order.
-- ------------------------------------------------------------
-- Order by employee names descending
SELECT *
FROM employee
ORDER BY employee_name DESC;

-- ------------------------------------------------------------
-- 13. display the list of employees in ascending order from
--     employee table.
-- ------------------------------------------------------------
-- Display employees in ascending order
SELECT *
FROM employee
ORDER BY employee_name ASC;
