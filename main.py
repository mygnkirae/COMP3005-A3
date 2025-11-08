"""
Simple PostgreSQL CRUD demo for the `students` table.

Functions implemented:
- getAllStudents()
- addStudent(first_name, last_name, email, enrollment_date)
- updateStudentEmail(student_id, new_email)
- deleteStudent(student_id)
"""

import os
import sys
import argparse
from typing import Optional, List, Tuple

import psycopg2
import psycopg2.extras
from psycopg2 import sql, IntegrityError


def get_connection(): #connection helper by opening psycopg2 connection using standard PG env vars
    """
    Connect using standard PG env vars:
    PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=int(os.getenv("PGPORT", "5432")),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", ""),
            dbname=os.getenv("PGDATABASE", "school"),
        )
        conn.autocommit = False  #managed to commit/rollback ourselves
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


def getAllStudents(conn) -> List[Tuple]: #CRUD: READ. retrieve all students ordered by student ID. uses a dictcursor for convenient column name access
    """ 
    Retrieve all students ordered by student_id.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT student_id, first_name, last_name, email, enrollment_date
            FROM students
            ORDER BY student_id;
        """)
        rows = cur.fetchall()
        return rows


def addStudent(conn, first_name: str, last_name: str, email: str, enrollment_date: Optional[str]) -> int: #CRUD: CREATE. 
    """
    Insert a new student. Returns the new student_id.
    enrollment_date should be 'YYYY-MM-DD' or None.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO students (first_name, last_name, email, enrollment_date)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id;
                """,
                (first_name, last_name, email, enrollment_date),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    except IntegrityError as ie:
        conn.rollback()
        #common mistake: duplicate email (unique violation)
        print(f"Insert failed (likely duplicate email): {ie}")
        raise
    except Exception as e:
        conn.rollback()
        print(f"Insert failed: {e}")
        raise


def updateStudentEmail(conn, student_id: int, new_email: str) -> bool: #CRUD: UPDATE. 
    """
    Update a student's email by student_id. Returns True if a row was updated. False if no match. Commits on success; rolls back and reraises on errors.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE students
                SET email = %s
                WHERE student_id = %s
                RETURNING student_id;
                """,
                (new_email, student_id),
            )
            updated = cur.fetchone()
        conn.commit()
        return updated is not None
    except IntegrityError as ie:
        conn.rollback()
        print(f"Update failed (likely duplicate email): {ie}") #unique email violation on update
        raise
    except Exception as e:
        conn.rollback()
        print(f"Update failed: {e}")
        raise


def deleteStudent(conn, student_id: int) -> bool: #CRUD: DELETE.
    """
    Delete a student by student_id. Returns True if a row was deleted.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM students
                WHERE student_id = %s
                RETURNING student_id;
                """,
                (student_id,),
            )
            deleted = cur.fetchone()
        conn.commit()
        return deleted is not None
    except Exception as e:
        conn.rollback()
        print(f"Delete failed: {e}")
        raise


def print_rows(rows: List[psycopg2.extras.DictRow]) -> None: #presentation helper
    """
    Pretty-print student rows to stdout for demo purposes.
    """
    if not rows:
        print("(no rows)")
        return
    for r in rows:
        print(
            f"[{r['student_id']:>3}] {r['first_name']} {r['last_name']} | "
            f"{r['email']} | {r['enrollment_date']}"
        )


def main(): #CLI argparse subcommands
    parser = argparse.ArgumentParser(description="Students CRUD CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list
    s_list = sub.add_parser("list", help="List all students")

    # add
    s_add = sub.add_parser("add", help="Add a student")
    s_add.add_argument("--first", required=True, help="First name")
    s_add.add_argument("--last", required=True, help="Last name")
    s_add.add_argument("--email", required=True, help="Email (must be unique)")
    s_add.add_argument("--date", default=None, help="Enrollment date YYYY-MM-DD (optional)")

    # update
    s_upd = sub.add_parser("update", help="Update a student's email")
    s_upd.add_argument("--id", type=int, required=True, help="student_id")
    s_upd.add_argument("--email", required=True, help="New email")

    # delete
    s_del = sub.add_parser("delete", help="Delete a student")
    s_del.add_argument("--id", type=int, required=True, help="student_id")

    args = parser.parse_args()
    conn = get_connection()

    if args.cmd == "list":
        rows = getAllStudents(conn)
        print_rows(rows)

    elif args.cmd == "add":
        new_id = addStudent(conn, args.first, args.last, args.email, args.date)
        print(f"Inserted student_id={new_id}")
        print_rows(getAllStudents(conn))

    elif args.cmd == "update":
        ok = updateStudentEmail(conn, args.id, args.email)
        print("Updated." if ok else "No matching student_id.")
        print_rows(getAllStudents(conn))

    elif args.cmd == "delete":
        ok = deleteStudent(conn, args.id)
        print("Deleted." if ok else "No matching student_id.")
        print_rows(getAllStudents(conn))

    conn.close()


if __name__ == "__main__":
    main()
