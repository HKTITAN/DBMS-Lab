-- ============================================================
-- DBMS Lab · 30-09-2026 · Experiment 6
-- Employee table: CREATE, seed 16 rows, then nested queries
-- Scalar subquery, IN, NOT IN, EXISTS, correlated subquery
-- Folder 30-09-2026-2: second experiment on 30 Sep 2026.
-- Microsoft SQL Server (T-SQL) — use this on the class server
-- Aggregate functions are Experiment 5 (30-09-2026).
--
-- Lab questions
-- 1. Create a table employee with the following attributes:
--    sr no, employee name, job, department, salary, city
-- 2. Insert 16 rows in the above mentioned table
-- 3. Display employees who earn more than the average salary
-- 4. Display the employee with the highest salary in each
--    department using a subquery
-- 5. Find the 2nd highest salary of the employees.
-- 6. Display employees who work in a department that has a
--    Professor, using IN
-- 7. Display employees who do not work in a department that
--    has a Professor, using NOT IN
-- 8. Display employees for whom there EXISTS a higher-paid
--    colleague in the same department
-- 9. Display employees who earn more than the average salary
--    of their own department (correlated subquery)
-- 10. Display the department whose total salary is the greatest
--     using a nested query
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
--    • same seed as Experiment 5 so the two labs compare
--    • Civil has no Professor, so NOT IN is non-empty
--    • the highest salary (92000) and the second-highest (90000)
--      are each earned by exactly one employee
--    • Neha Gupta (ECE, 58000) is above the company average
--      and below the ECE average
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
-- 3. Display the employee name, department and salary of
--    employees who earn more than the average salary,
--    using a nested query
-- ------------------------------------------------------------
-- Employees earning more than the average salary
SELECT employee_name, department, salary
FROM employee
WHERE salary > (SELECT AVG(salary) FROM employee)
ORDER BY salary DESC;

-- ------------------------------------------------------------
-- 4. Display the employee with the highest salary in each
--    department using a subquery
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
-- 5. Find the 2nd highest salary of the employees.
-- ------------------------------------------------------------
-- Find the 2nd highest salary of the employees.
SELECT MAX(salary)
FROM employee
WHERE salary < (SELECT MAX(salary) FROM employee);

-- ------------------------------------------------------------
-- 6. Display employees who work in a department that has a
--    Professor, using IN and a subquery
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
-- 7. Display employees who do not work in a department that
--    has a Professor, using NOT IN and a subquery
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
-- 8. Display employees for whom there EXISTS a higher-paid
--    colleague in the same department (correlated subquery)
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
-- 9. Display employees who earn more than the average salary
--    of their own department (correlated subquery)
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

-- ------------------------------------------------------------
-- 10. Display the department whose total salary is the
--     greatest, using a nested query
-- ------------------------------------------------------------
-- Department with the greatest total salary
SELECT department,
       SUM(salary) AS total_salary
FROM employee
GROUP BY department
HAVING SUM(salary) = (
    SELECT MAX(total_salary)
    FROM (
        SELECT SUM(salary) AS total_salary
        FROM employee
        GROUP BY department
    ) AS dept_totals
);
