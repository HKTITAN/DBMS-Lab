-- ============================================================
-- DBMS Lab · 09-09-2026
-- Employee table: CREATE, seed 10 rows, then SELECT queries
-- DISTINCT, WHERE, BETWEEN, IN, ORDER BY
-- Then CSE / Mechanical student tables: UNION, UNION ALL, INTERSECT
-- Microsoft SQL Server (T-SQL) — use this on the class server
--
-- Lab questions (1(a)/1(b) = sheet's two "1." items; "distant" = DISTINCT)
-- 1(a). Create a table employee with the following attributes:
--       sr no, employee name, job, manager, hire date, salary,
--       department no, city
-- 1(b). Insert 10 rows in the above mentioned table
-- 2. SELECT all the details from the employee table
-- 3. Select only DISTINCT department number from employee table
--    (lab sheet wrote "distant")
-- 4. SELECT all department numbers from the employee table
-- 5. SELECT employee name, salary WHERE salary is > 30000 rs
--    from the employee table
-- 6. SELECT employee name, hire date WHERE city is not Delhi
--    from the employee table
-- 7. SELECT employee name, hire date WHERE city is either
--    Delhi or Mumbai from the employee table
-- 8. SELECT employee number, employee name WHERE salary is
--    BETWEEN 30000 rs and 50000 rs
-- 9. SELECT employee number, employee name WHERE salary is
--    NOT BETWEEN 30000 and 50000 from the employee table
-- 10. SELECT all the details WHERE city is among the following:
--     Delhi, Mumbai, Chennai, Bangalore
-- 11. SELECT all the details WHERE city is not Mumbai, Delhi
--     or Chennai from the employee table
-- 12. SELECT all the details from the employee table and
--     ORDER BY employee names in descending order
-- 13. Display the list of employees in ascending order from
--     the employee table.
-- 14. Create a table cse (CSE students) with roll no, student name, city
-- 15. Insert 5 rows in the cse table
-- 16. Create a table mechanical (Mechanical students) with the same attributes
-- 17. Insert 5 rows in the mechanical table
--     (two rows also appear in cse so INTERSECT is non-empty)
-- 18. SELECT all the details from the cse table
-- 19. SELECT all the details from the mechanical table
-- 20. SELECT the UNION of cse and mechanical
-- 21. SELECT the UNION ALL of cse and mechanical
-- 22. SELECT the INTERSECT of cse and mechanical
-- ============================================================

DROP TABLE IF EXISTS employee;

-- ------------------------------------------------------------
-- 1(a). Create a table employee with the following attributes:
--       sr no, employee name, job, manager, hire date, salary,
--       department no, city
-- ------------------------------------------------------------
CREATE TABLE employee (
    sr_no          INT PRIMARY KEY,
    employee_name  VARCHAR(100) NOT NULL,
    job            VARCHAR(50) NOT NULL,
    manager        VARCHAR(100) NULL,
    hire_date      DATE NOT NULL,
    salary         NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    department_no  INT NOT NULL,
    city           VARCHAR(50) NOT NULL
);

-- ------------------------------------------------------------
-- 1(b). Insert 10 rows in the above mentioned table
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
-- 3. Select only DISTINCT department number from employee table
--    (lab sheet wrote "distant")
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

-- ============================================================
-- CSE / Mechanical student tables — UNION, UNION ALL, INTERSECT
-- Compatible columns (roll_no, student_name, city). Two identical
-- rows appear in both tables so INTERSECT returns a non-empty set.
-- ============================================================

DROP TABLE IF EXISTS cse;
DROP TABLE IF EXISTS mechanical;

-- ------------------------------------------------------------
-- 14. Create a table cse (CSE students) with the following
--     attributes: roll no, student name, city
-- ------------------------------------------------------------
CREATE TABLE cse (
    roll_no        INT PRIMARY KEY,
    student_name   VARCHAR(100) NOT NULL,
    city           VARCHAR(50) NOT NULL
);

-- ------------------------------------------------------------
-- 15. Insert 5 rows in the cse table
-- ------------------------------------------------------------
INSERT INTO cse (roll_no, student_name, city)
VALUES
    (1, 'Amit Verma',   'Delhi'),
    (2, 'Rahul Das',    'Kolkata'),
    (3, 'Sneha Reddy',  'Hyderabad'),
    (4, 'Isha Kapoor',  'Chandigarh'),
    (5, 'Dev Patel',    'Ahmedabad');

-- ------------------------------------------------------------
-- 16. Create a table mechanical (Mechanical students) with the
--     following attributes: roll no, student name, city
-- ------------------------------------------------------------
CREATE TABLE mechanical (
    roll_no        INT PRIMARY KEY,
    student_name   VARCHAR(100) NOT NULL,
    city           VARCHAR(50) NOT NULL
);

-- ------------------------------------------------------------
-- 17. Insert 5 rows in the mechanical table
--     Two rows match cse (Amit Verma / Delhi, Sneha Reddy / Hyderabad)
-- ------------------------------------------------------------
INSERT INTO mechanical (roll_no, student_name, city)
VALUES
    (1, 'Amit Verma',   'Delhi'),
    (3, 'Sneha Reddy',  'Hyderabad'),
    (6, 'Mohit Jain',   'Jaipur'),
    (7, 'Kavya Menon',  'Kochi'),
    (8, 'Tushar Rao',   'Nagpur');

-- ------------------------------------------------------------
-- 18. SELECT all the details from the cse table
-- ------------------------------------------------------------
-- All the details from CSE
SELECT * FROM cse;

-- ------------------------------------------------------------
-- 19. SELECT all the details from the mechanical table
-- ------------------------------------------------------------
-- All the details from Mechanical
SELECT * FROM mechanical;

-- ------------------------------------------------------------
-- 20. SELECT the UNION of cse and mechanical
--     (unique rows from either table)
-- ------------------------------------------------------------
-- UNION of CSE and Mechanical
SELECT * FROM cse
UNION
SELECT * FROM mechanical
ORDER BY roll_no;

-- ------------------------------------------------------------
-- 21. SELECT the UNION ALL of cse and mechanical
--     (all rows, including duplicates)
-- ------------------------------------------------------------
-- UNION ALL of CSE and Mechanical
SELECT * FROM cse
UNION ALL
SELECT * FROM mechanical
ORDER BY roll_no;

-- ------------------------------------------------------------
-- 22. SELECT the INTERSECT of cse and mechanical
--     (rows that appear in both tables)
-- ------------------------------------------------------------
-- INTERSECT of CSE and Mechanical
SELECT * FROM cse
INTERSECT
SELECT * FROM mechanical
ORDER BY roll_no;
