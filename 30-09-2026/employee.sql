-- ============================================================
-- DBMS Lab · 30-09-2026
-- Employee table: CREATE, seed 16 rows, then aggregate functions
-- and nested queries.
-- SUM, AVG, MAX, MIN, COUNT, GROUP BY, HAVING
-- Subqueries: scalar, IN, NOT IN, EXISTS, correlated
-- SQLite  (sql.js compiler / DB Browser / sqlite3)
-- For the class SQL Server, run employee.sqlserver.sql instead.
--
-- Lab questions
-- 1. Create a table employee with the following attributes:
--    sr no, employee name, job, department, salary, city
-- 2. Insert 16 rows in the above mentioned table
-- 3. Display the total number of employees using COUNT
-- 4. Display the total salary of all employees using SUM
-- 5. Display the average salary of all employees using AVG
-- 6. Display the maximum and minimum salary using MAX and MIN
-- 7. For each department, display COUNT, SUM, AVG, MAX and MIN
--    using GROUP BY
-- 8. Display departments whose average salary is greater than
--    55000 using GROUP BY and HAVING
-- 9. Display departments that have more than 3 employees
--    using GROUP BY and HAVING
-- 10. Display employees who earn more than the average salary
--     (nested query)
-- 11. Display the employee with the highest salary in each
--     department using a subquery
-- 12. Display the employee who earns the second-highest salary
--     using a nested query
-- 13. Display employees who work in a department that has a
--     Professor, using IN and a subquery
-- 14. Display employees who do not work in a department that
--     has a Professor, using NOT IN and a subquery
-- 15. Display employees for whom there EXISTS a higher-paid
--     colleague in the same department (correlated)
-- 16. Display employees who earn more than the average salary
--     of their own department (correlated subquery)
-- ============================================================

DROP TABLE IF EXISTS employee;

-- ------------------------------------------------------------
-- 1. Create a table employee with the following attributes:
--    sr no, employee name, job, department, salary, city
-- ------------------------------------------------------------
CREATE TABLE employee (
    sr_no          INTEGER PRIMARY KEY,
    employee_name  TEXT NOT NULL,
    job            TEXT NOT NULL,
    department     TEXT NOT NULL,
    salary         NUMERIC(10, 2) NOT NULL CHECK (salary > 0),
    city           TEXT NOT NULL
);

-- ------------------------------------------------------------
-- 2. Insert 16 rows in the above mentioned table
--    • four departments: CSE (5), Mechanical (4), ECE (4), Civil (3)
--    • Civil has no Professor, so NOT IN is non-empty
--    • salaries vary so SUM, AVG, MAX, MIN and HAVING differ
--    • the overall maximum (92000) and second maximum (90000)
--      are each earned by exactly one employee
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
-- 4. Display the total salary of all employees from the
--    employee table using SUM
-- ------------------------------------------------------------
-- Total salary of all employees
SELECT SUM(salary) AS total_salary
FROM employee;

-- ------------------------------------------------------------
-- 5. Display the average salary of all employees from the
--    employee table using AVG
-- ------------------------------------------------------------
-- Average salary of all employees
SELECT AVG(salary) AS average_salary
FROM employee;

-- ------------------------------------------------------------
-- 6. Display the maximum and minimum salary from the employee
--    table using MAX and MIN
-- ------------------------------------------------------------
-- Maximum and minimum salary
SELECT MAX(salary) AS maximum_salary,
       MIN(salary) AS minimum_salary
FROM employee;

-- ------------------------------------------------------------
-- 7. Display the number of employees, total salary, average
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
-- 8. Display the department and average salary of departments
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
-- 9. Display the department and the number of employees for
--    departments that have more than 3 employees using
--    GROUP BY and HAVING
-- ------------------------------------------------------------
-- Departments with more than 3 employees
SELECT department,
       COUNT(*) AS employee_count
FROM employee
GROUP BY department
HAVING COUNT(*) > 3
ORDER BY department;

-- ------------------------------------------------------------
-- 10. Display the employee name, department and salary of
--     employees who earn more than the average salary,
--     using a nested query
-- ------------------------------------------------------------
-- Employees earning more than the average salary
SELECT employee_name, department, salary
FROM employee
WHERE salary > (SELECT AVG(salary) FROM employee)
ORDER BY salary DESC;

-- ------------------------------------------------------------
-- 11. Display the employee with the highest salary in each
--     department using a subquery
-- ------------------------------------------------------------
-- Highest salary in each department
SELECT e.employee_name, e.department, e.salary
FROM employee AS e
WHERE e.salary = (
    SELECT MAX(c.salary)
    FROM employee AS c
    WHERE c.department = e.department
)
ORDER BY e.department;

-- ------------------------------------------------------------
-- 12. Display the employee name, department and salary of the
--     employee who earns the second-highest salary, using a
--     nested query
-- ------------------------------------------------------------
-- Second-highest salary
SELECT employee_name, department, salary AS second_highest_salary
FROM employee
WHERE salary = (
    SELECT MAX(salary)
    FROM employee
    WHERE salary < (SELECT MAX(salary) FROM employee)
);

-- ------------------------------------------------------------
-- 13. Display employees who work in a department that has a
--     Professor, using IN and a subquery
-- ------------------------------------------------------------
-- Employees in a department that has a Professor
SELECT employee_name, job, department, salary
FROM employee
WHERE department IN (
    SELECT department
    FROM employee
    WHERE job = 'Professor'
)
ORDER BY department, employee_name;

-- ------------------------------------------------------------
-- 14. Display employees who do not work in a department that
--     has a Professor, using NOT IN and a subquery
-- ------------------------------------------------------------
-- Employees not in a department that has a Professor
SELECT employee_name, job, department, salary
FROM employee
WHERE department NOT IN (
    SELECT department
    FROM employee
    WHERE job = 'Professor'
)
ORDER BY department, employee_name;

-- ------------------------------------------------------------
-- 15. Display employees for whom there EXISTS a higher-paid
--     colleague in the same department (correlated subquery)
-- ------------------------------------------------------------
-- Employees with a higher-paid colleague
SELECT e.employee_name, e.department, e.salary
FROM employee AS e
WHERE EXISTS (
    SELECT 1
    FROM employee AS c
    WHERE c.department = e.department
      AND c.salary > e.salary
)
ORDER BY e.department, e.salary DESC;

-- ------------------------------------------------------------
-- 16. Display employees who earn more than the average salary
--     of their own department (correlated subquery)
-- ------------------------------------------------------------
-- Employees above their department average
SELECT e.employee_name, e.department, e.salary
FROM employee AS e
WHERE e.salary > (
    SELECT AVG(d.salary)
    FROM employee AS d
    WHERE d.department = e.department
)
ORDER BY e.department, e.salary DESC;
