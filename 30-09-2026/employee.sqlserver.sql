-- ============================================================
-- DBMS Lab · 30-09-2026 · Experiment 5
-- Employee table: CREATE, seed 16 rows, then aggregate functions
-- SUM, AVG, MAX, MIN, COUNT, GROUP BY, HAVING
-- Microsoft SQL Server (T-SQL) — use this on the class server
-- Nested queries are Experiment 6 (30-09-2026-2).
--
-- Lab questions
-- 1. Create a table employee with the following attributes:
--    sr no, employee name, job, department, salary, city
-- 2. Insert 16 rows in the above mentioned table
-- 3. Display the total number of employees using COUNT
-- 4. Display the number of distinct departments using COUNT
-- 5. Display the total salary of all employees using SUM
-- 6. Display the average salary of all employees using AVG
-- 7. Display the maximum and minimum salary using MAX and MIN
-- 8. For each department, display COUNT, SUM, AVG, MAX and MIN
--    using GROUP BY
-- 9. Display departments whose average salary is greater than
--    55000 using GROUP BY and HAVING
-- 10. Display departments that have more than 3 employees
--     using GROUP BY and HAVING
-- 11. Display the number of employees, total salary and average
--     salary of the CSE department
-- 12. Display cities that have more than one employee using
--     GROUP BY and HAVING
-- ============================================================

DROP TABLE IF EXISTS employee;

-- ------------------------------------------------------------
-- 1. Create a table employee with the following attributes:
--    sr no, employee name, job, department, salary, city
-- ------------------------------------------------------------
CREATE TABLE employee (
    sr_no          INT PRIMARY KEY,
    employee_name  VARCHAR(100) NOT NULL,
    job            VARCHAR(50) NOT NULL,
    department     VARCHAR(50) NOT NULL,
    salary         NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    city           VARCHAR(50) NOT NULL
);

-- ------------------------------------------------------------
-- 2. Insert 16 rows in the above mentioned table
--    • four departments: CSE (5), Mechanical (4), ECE (4), Civil (3)
--    • salaries vary so SUM, AVG, MAX, MIN and HAVING differ
--    • five cities have two employees; the rest have one
-- ------------------------------------------------------------
INSERT INTO employee
    (sr_no, employee_name, job, department, salary, city)
VALUES
    (1,  'Rajesh Kumar',  'Professor',            'CSE',         92000.00, 'Delhi'),
    (2,  'Ananya Sharma', 'Associate Professor',  'CSE',         78000.00, 'Bangalore'),
    (3,  'Fatima Khan',   'Assistant Professor',  'CSE',         56000.00, 'Bangalore'),
    (4,  'Karan Iyer',    'Lab Instructor',       'CSE',         42000.00, 'Mumbai'),
    (5,  'Dev Patel',     'Teaching Assistant',   'CSE',         28000.00, 'Ahmedabad'),
    (6,  'Vikram Singh',  'Professor',            'Mechanical',  88000.00, 'Hyderabad'),
    (7,  'Rohan Mehta',   'Associate Professor',  'Mechanical',  64000.00, 'Mumbai'),
    (8,  'Arjun Patel',   'Assistant Professor',  'Mechanical',  48000.00, 'Pune'),
    (9,  'Mohit Jain',    'Lab Instructor',       'Mechanical',  32000.00, 'Jaipur'),
    (10, 'Priya Nair',    'Professor',            'ECE',         90000.00, 'Chennai'),
    (11, 'Neha Gupta',    'Associate Professor',  'ECE',         58000.00, 'Delhi'),
    (12, 'Meera Joshi',   'Assistant Professor',  'ECE',         51000.00, 'Chennai'),
    (13, 'Kavya Menon',   'Lab Instructor',       'ECE',         36000.00, 'Kochi'),
    (14, 'Sneha Reddy',   'Associate Professor',  'Civil',       60000.00, 'Hyderabad'),
    (15, 'Rahul Das',     'Assistant Professor',  'Civil',       45000.00, 'Kolkata'),
    (16, 'Tushar Rao',    'Lab Instructor',       'Civil',       30000.00, 'Nagpur');

-- ------------------------------------------------------------
-- 3. Display the total number of employees from the employee
--    table using COUNT
-- ------------------------------------------------------------
-- Total number of employees
SELECT COUNT(*) AS employee_count
FROM employee;

-- ------------------------------------------------------------
-- 4. Display the number of distinct departments using COUNT
-- ------------------------------------------------------------
-- Number of distinct departments
SELECT COUNT(DISTINCT department) AS department_count
FROM employee;

-- ------------------------------------------------------------
-- 5. Display the total salary of all employees from the
--    employee table using SUM
-- ------------------------------------------------------------
-- Total salary of all employees
SELECT SUM(salary) AS total_salary
FROM employee;

-- ------------------------------------------------------------
-- 6. Display the average salary of all employees from the
--    employee table using AVG
-- ------------------------------------------------------------
-- Average salary of all employees
SELECT AVG(salary) AS average_salary
FROM employee;

-- ------------------------------------------------------------
-- 7. Display the maximum and minimum salary from the employee
--    table using MAX and MIN
-- ------------------------------------------------------------
-- Maximum and minimum salary
SELECT MAX(salary) AS maximum_salary,
       MIN(salary) AS minimum_salary
FROM employee;

-- ------------------------------------------------------------
-- 8. Display the number of employees, total salary, average
--    salary, highest salary and lowest salary of each
--    department using COUNT, SUM, AVG, MAX, MIN and GROUP BY
-- ------------------------------------------------------------
-- Aggregates for each department
SELECT department,
       COUNT(*)    AS employee_count,
       SUM(salary) AS total_salary,
       AVG(salary) AS average_salary,
       MAX(salary) AS highest_salary,
       MIN(salary) AS lowest_salary
FROM employee
GROUP BY department
ORDER BY department;

-- ------------------------------------------------------------
-- 9. Display the department and average salary of departments
--    whose average salary is greater than 55000 using
--    GROUP BY and HAVING
-- ------------------------------------------------------------
-- Departments with average salary above 55000
SELECT department,
       AVG(salary) AS average_salary
FROM employee
GROUP BY department
HAVING AVG(salary) > 55000
ORDER BY department;

-- ------------------------------------------------------------
-- 10. Display the department and the number of employees for
--     departments that have more than 3 employees using
--     GROUP BY and HAVING
-- ------------------------------------------------------------
-- Departments with more than 3 employees
SELECT department,
       COUNT(*) AS employee_count
FROM employee
GROUP BY department
HAVING COUNT(*) > 3
ORDER BY department;

-- ------------------------------------------------------------
-- 11. Display the number of employees, total salary and
--     average salary of the CSE department
-- ------------------------------------------------------------
-- CSE department aggregates
SELECT COUNT(*)    AS employee_count,
       SUM(salary) AS total_salary,
       AVG(salary) AS average_salary
FROM employee
WHERE department = 'CSE';

-- ------------------------------------------------------------
-- 12. Display cities that have more than one employee using
--     GROUP BY and HAVING
-- ------------------------------------------------------------
-- Cities with more than one employee
SELECT city,
       COUNT(*) AS employee_count
FROM employee
GROUP BY city
HAVING COUNT(*) > 1
ORDER BY city;
