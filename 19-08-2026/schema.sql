-- ============================================================
-- Employee Directory — schema
-- SQLite dialect. Runs as-is in the in-browser SQL Compiler
-- (index.html), and in the sqlite3 CLI / DB Browser for SQLite.
-- ============================================================

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS employee_directory;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- ------------------------------------------------------------
-- departments
-- ------------------------------------------------------------
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    description   TEXT,
    color_hex     TEXT NOT NULL DEFAULT '#1CB0F6'
);

-- ------------------------------------------------------------
-- employees
-- ------------------------------------------------------------
CREATE TABLE employees (
    employee_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    email             TEXT NOT NULL UNIQUE,
    job_title         TEXT NOT NULL,
    department_id     INTEGER NOT NULL REFERENCES departments (department_id) ON DELETE RESTRICT,
    manager_id        INTEGER REFERENCES employees (employee_id) ON DELETE SET NULL,
    salary            NUMERIC(10,2) NOT NULL CHECK (salary > 0),
    hire_date         TEXT NOT NULL,
    employment_status TEXT NOT NULL DEFAULT 'active'
                        CHECK (employment_status IN ('active', 'remote', 'on_leave')),
    avatar_seed       TEXT NOT NULL
);

CREATE INDEX idx_employees_department ON employees (department_id);
CREATE INDEX idx_employees_manager    ON employees (manager_id);

-- ------------------------------------------------------------
-- employee_directory — flattened view joining department + manager.
-- Convenient for reporting queries and reused by the frontend.
-- ------------------------------------------------------------
CREATE VIEW employee_directory AS
SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.job_title,
    d.name                             AS department_name,
    d.color_hex                        AS department_color,
    m.first_name || ' ' || m.last_name AS manager_name,
    e.salary,
    e.hire_date,
    e.employment_status,
    e.avatar_seed
FROM employees e
JOIN departments d ON d.department_id = e.department_id
LEFT JOIN employees m ON m.employee_id = e.manager_id;
