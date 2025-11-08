# COMP3005 A3 – PostgreSQL CRUD (students)

Implements the required CRUD functions against a PostgreSQL `students` table using parameterized SQL and explicit transactions.

- `getAllStudents()` → READ
- `addStudent(first, last, email, date)` → CREATE
- `updateStudentEmail(id, new_email)` → UPDATE
- `deleteStudent(id)` → DELETE

## Prerequisites
- PostgreSQL (any recent version)
- Python 3.11+ (or 3.10+)
- `psycopg2-binary` (installed via `requirements.txt`)

## Setup 
Create DB/table + seed to run in your SQLTools on your own DB
    ```sql
   CREATE TABLE IF NOT EXISTS students (
     student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
     first_name TEXT NOT NULL,
     last_name  TEXT NOT NULL,
     email      TEXT NOT NULL UNIQUE,
     enrollment_date DATE
   );
   INSERT INTO students (first_name,last_name,email,enrollment_date) VALUES
   ('John','Doe','john.doe@example.com','2023-09-01'),
   ('Jane','Smith','jane.smith@example.com','2023-09-01'),
   ('Jim','Beam','jim.beam@example.com','2023-09-02')
   ON CONFLICT (email) DO NOTHING;

## Python env
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt

## Run (pick one)
# A) Using env vars
export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=<your-pass> PGDATABASE=comp3005_a3
python main.py list

# B) Using flags (if you added flag support)
python main.py --host localhost --port 5432 --user postgres --password <your-pass> --db comp3005_a3 list

## Commands
# READ
python main.py list
# CREATE
python main.py add --first "Bella" --last "Night" --email "abella.night@example.com" --date 2023-09-04
# UPDATE
python main.py update --id 1 --email "johnny.doe@example.com"
# DELETE
python main.py delete --id 3

## Video link 
Video link: https://youtu.be/zGZyMPraLmo 
