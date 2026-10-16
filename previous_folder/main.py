import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date, time
import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Employee Management System",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "employee_management.db"


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    # timeout বাড়িয়ে ৫ সেকেন্ড করা হলো যাতে লক রিলিজ হওয়ার জন্য একটু অপেক্ষা করতে পারে
    conn = sqlite3.connect(DB_FILE, timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def execute(query, params=(), fetch=False, many=False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if many:
            cur.executemany(query, params)
        else:
            cur.execute(query, params)

        if fetch:
            result = cur.fetchall()
            return result

        conn.commit()
        last_id = cur.lastrowid
        return last_id
    finally:
        # কুয়েরি সফল হোক বা এরর আসুক, কানেকশন যেন অবশ্যই বন্ধ হয়
        cur.close()
        conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Employee',
            employee_id INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            emergency_contact TEXT,
            department_id INTEGER,
            designation TEXT,
            joining_date TEXT,
            salary REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TEXT,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            status TEXT,
            working_hours REAL DEFAULT 0,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            applied_at TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            month TEXT,
            basic_salary REAL,
            allowance REAL DEFAULT 0,
            bonus REAL DEFAULT 0,
            deduction REAL DEFAULT 0,
            overtime REAL DEFAULT 0,
            net_salary REAL,
            generated_at TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            employee_id INTEGER,
            deadline TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            created_at TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            review_date TEXT,
            rating REAL,
            kpi TEXT,
            feedback TEXT,
            reviewer TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            document_name TEXT,
            file_path TEXT,
            uploaded_at TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            title TEXT,
            message TEXT,
            created_at TEXT,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            created_at TEXT
        )
        """
    ]

    for table in tables:
        execute(table)

    # Default departments
    departments = [
        ("Human Resources", "HR Department"),
        ("IT", "Information Technology"),
        ("Finance", "Finance and Accounts"),
        ("Marketing", "Marketing Department"),
        ("Operations", "Operations Department"),
    ]

    for name, description in departments:
        try:
            execute(
                "INSERT INTO departments(name, description) VALUES (?, ?)",
                (name, description)
            )
        except sqlite3.IntegrityError:
            pass

    # Default admin
    try:
        execute(
            """
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
            """,
            ("admin", hash_password("admin123"), "Admin")
        )
    except sqlite3.IntegrityError:
        pass


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(username, password):
    user = execute(
        """
        SELECT * FROM users
        WHERE username = ? AND password = ?
        """,
        (username, hash_password(password)),
        fetch=True
    )
    return user[0] if user else None


def log_action(username, action):
    execute(
        """
        INSERT INTO audit_logs(username, action, created_at)
        VALUES (?, ?, ?)
        """,
        (
            username,
            action,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )


# ============================================================
# LOGIN
# ============================================================

def login_page():
    st.title("👨‍💼 Employee Management System")
    st.subheader("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            user = authenticate(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = dict(user)

                log_action(
                    username,
                    "Logged into the system"
                )

                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.info(
        "Default Admin Login → Username: admin | Password: admin123"
    )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():
    user = st.session_state.user

    st.sidebar.title("🏢 EMS")
    st.sidebar.write(f"👤 **{user['username']}**")
    st.sidebar.write(f"Role: **{user['role']}**")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Employees",
            "Departments",
            "Attendance",
            "Leave Management",
            "Payroll",
            "Tasks",
            "Performance",
            "Documents",
            "Notifications",
            "Audit Logs"
        ]
    )

    if st.sidebar.button("🚪 Logout"):
        log_action(
            user["username"],
            "Logged out"
        )
        st.session_state.clear()
        st.rerun()

    return menu


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():
    st.title("📊 Dashboard")

    total_employees = execute(
        "SELECT COUNT(*) AS c FROM employees",
        fetch=True
    )[0]["c"]

    active_employees = execute(
        """
        SELECT COUNT(*) AS c
        FROM employees
        WHERE status = 'Active'
        """,
        fetch=True
    )[0]["c"]

    today = date.today().isoformat()

    present_today = execute(
        """
        SELECT COUNT(*) AS c
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
        """,
        (today,),
        fetch=True
    )[0]["c"]

    pending_leave = execute(
        """
        SELECT COUNT(*) AS c
        FROM leave_requests
        WHERE status = 'Pending'
        """,
        fetch=True
    )[0]["c"]

    pending_tasks = execute(
        """
        SELECT COUNT(*) AS c
        FROM tasks
        WHERE status != 'Completed'
        """,
        fetch=True
    )[0]["c"]

    payroll = execute(
        """
        SELECT COALESCE(SUM(net_salary),0) AS total
        FROM payroll
        """,
        fetch=True
    )[0]["total"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Employees", total_employees)
    col2.metric("Active Employees", active_employees)
    col3.metric("Present Today", present_today)
    col4.metric("Pending Leave", pending_leave)

    col5, col6 = st.columns(2)
    col5.metric("Pending Tasks", pending_tasks)
    col6.metric("Total Payroll", f"{payroll:,.2f}")

    st.divider()
    st.subheader("Department Statistics")

    data = execute(
        """
        SELECT d.name AS Department,
               COUNT(e.id) AS Employees
        FROM departments d
        LEFT JOIN employees e
        ON d.id = e.department_id
        GROUP BY d.id
        """,
        fetch=True
    )

    if data:
        df = pd.DataFrame([dict(row) for row in data])
        st.bar_chart(df.set_index("Department"))


# ============================================================
# EMPLOYEES
# ============================================================

def employees_page():
    st.title("👨‍💼 Employee Management")

    tab1, tab2, tab3 = st.tabs(
        [
            "➕ Add Employee",
            "👥 Employee List",
            "✏️ Update / Delete"
        ]
    )

    departments = execute(
        "SELECT * FROM departments",
        fetch=True
    )

    department_map = {
        row["name"]: row["id"]
        for row in departments
    }

    with tab1:
        with st.form("employee_form"):
            c1, c2 = st.columns(2)

            first_name = c1.text_input("First Name *")
            last_name = c2.text_input("Last Name")

            email = c1.text_input("Email")
            phone = c2.text_input("Phone")

            address = st.text_area("Address")
            emergency = st.text_input("Emergency Contact")

            department = st.selectbox(
                "Department",
                list(department_map.keys())
            )

            designation = st.text_input("Designation")
            joining_date = st.date_input("Joining Date", date.today())
            salary = st.number_input("Basic Salary", min_value=0.0, step=1000.0)

            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if not first_name.strip():
                    st.error("First name is required.")
                else:
                    employee_code = (
                        "EMP-" + datetime.now().strftime("%Y%m%d%H%M%S")
                    )

                    try:
                        employee_id = execute(
                            """
                            INSERT INTO employees(
                                employee_code, first_name, last_name, email,
                                phone, address, emergency_contact, department_id,
                                designation, joining_date, salary, created_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                employee_code,
                                first_name,
                                last_name,
                                email,
                                phone,
                                address,
                                emergency,
                                department_map[department],
                                designation,
                                joining_date.isoformat(),
                                salary,
                                datetime.now().isoformat()
                            )
                        )

                        username = employee_code.lower()

                        try:
                            execute(
                                """
                                INSERT INTO users(
                                    username, password, role, employee_id
                                )
                                VALUES (?, ?, ?, ?)
                                """,
                                (
                                    username,
                                    hash_password("123456"),
                                    "Employee",
                                    employee_id
                                )
                            )
                        except sqlite3.IntegrityError:
                            pass

                        st.success(
                            f"""
                            Employee created successfully.
                            Employee ID: {employee_code}
                            Default username: {username}
                            Default password: 123456
                            """
                        )

                        log_action(
                            st.session_state.user["username"],
                            f"Created employee {employee_code}"
                        )

                    except sqlite3.IntegrityError:
                        st.error("Employee could not be created.")

    with tab2:
        data = execute(
            """
            SELECT
                e.id,
                e.employee_code AS Employee_ID,
                e.first_name || ' ' || COALESCE(e.last_name,'') AS Name,
                e.email AS Email,
                e.phone AS Phone,
                d.name AS Department,
                e.designation AS Designation,
                e.joining_date AS Joining_Date,
                e.salary AS Salary,
                e.status AS Status
            FROM employees e
            LEFT JOIN departments d
            ON e.department_id = d.id
            ORDER BY e.id DESC
            """,
            fetch=True
        )

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Export CSV", csv, "employees.csv", "text/csv")
        else:
            st.info("No employees found.")

    with tab3:
        data = execute(
            """
            SELECT id, employee_code, first_name, last_name
            FROM employees
            ORDER BY id
            """,
            fetch=True
        )

        if not data:
            st.info("No employees.")
        else:
            options = {
                f"{x['employee_code']} - {x['first_name']} {x['last_name'] or ''}": x["id"]
                for x in data
            }

            selected = st.selectbox("Select Employee", list(options.keys()))
            employee_id = options[selected]

            emp = execute(
                "SELECT * FROM employees WHERE id=?",
                (employee_id,),
                fetch=True
            )[0]

            with st.form("update_employee"):
                first = st.text_input("First Name", emp["first_name"])
                last = st.text_input("Last Name", emp["last_name"] or "")
                email = st.text_input("Email", emp["email"] or "")
                phone = st.text_input("Phone", emp["phone"] or "")
                designation = st.text_input("Designation", emp["designation"] or "")
                salary = st.number_input("Salary", value=float(emp["salary"] or 0))
                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if emp["status"] == "Active" else 1
                )

                update = st.form_submit_button("Update Employee")

                if update:
                    execute(
                        """
                        UPDATE employees
                        SET first_name=?, last_name=?, email=?, phone=?,
                            designation=?, salary=?, status=?
                        WHERE id=?
                        """,
                        (first, last, email, phone, designation, salary, status, employee_id)
                    )
                    st.success("Employee updated successfully.")

            if st.button("🗑️ Delete Selected Employee"):
                execute("DELETE FROM employees WHERE id=?", (employee_id,))
                st.warning("Employee deleted.")
                st.rerun()


# ============================================================
# DEPARTMENTS
# ============================================================

def departments_page():
    st.title("🏢 Department Management")

    with st.form("department_form"):
        name = st.text_input("Department Name")
        description = st.text_area("Description")
        submit = st.form_submit_button("Create Department")

        if submit:
            try:
                execute(
                    "INSERT INTO departments(name, description) VALUES (?, ?)",
                    (name, description)
                )
                st.success("Department created.")
            except sqlite3.IntegrityError:
                st.error("Department already exists.")

    data = execute("SELECT * FROM departments", fetch=True)
    if data:
        df = pd.DataFrame([dict(x) for x in data])
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# ATTENDANCE
# ============================================================

def attendance_page():
    st.title("🕐 Attendance Management")

    employees = execute(
        "SELECT id, employee_code, first_name, last_name FROM employees WHERE status='Active'",
        fetch=True
    )

    if not employees:
        st.warning("Add employees first.")
        return

    options = {
        f"{x['employee_code']} - {x['first_name']} {x['last_name'] or ''}": x["id"]
        for x in employees
    }

    selected = st.selectbox("Employee", list(options.keys()))
    employee_id = options[selected]

    attendance_date = st.date_input("Date", date.today())
    c1, c2 = st.columns(2)
    check_in = c1.time_input("Check In", time(9, 0))
    check_out = c2.time_input("Check Out", time(17, 0))

    status = st.selectbox("Status", ["Present", "Absent", "Late", "Half Day", "Leave"])

    if st.button("Save Attendance"):
        start = datetime.combine(attendance_date, check_in)
        end = datetime.combine(attendance_date, check_out)
        hours = max(0, (end - start).seconds / 3600)

        existing = execute(
            "SELECT id FROM attendance WHERE employee_id=? AND attendance_date=?",
            (employee_id, attendance_date.isoformat()),
            fetch=True
        )

        if existing:
            execute(
                """
                UPDATE attendance
                SET check_in=?, check_out=?, status=?, working_hours=?
                WHERE id=?
                """,
                (check_in.strftime("%H:%M"), check_out.strftime("%H:%M"), status, hours, existing[0]["id"])
            )
        else:
            execute(
                """
                INSERT INTO attendance(
                    employee_id, attendance_date, check_in, check_out, status, working_hours
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (employee_id, attendance_date.isoformat(), check_in.strftime("%H:%M"), check_out.strftime("%H:%M"), status, hours)
            )

        st.success("Attendance saved.")

    st.divider()

    data = execute(
        """
        SELECT
            a.attendance_date AS Date,
            e.employee_code AS Employee,
            e.first_name || ' ' || COALESCE(e.last_name,'') AS Name,
            a.check_in AS Check_In,
            a.check_out AS Check_Out,
            a.status AS Status,
            a.working_hours AS Working_Hours
        FROM attendance a
        JOIN employees e
        ON e.id=a.employee_id
        ORDER BY a.attendance_date DESC
        """,
        fetch=True
    )

    if data:
        df = pd.DataFrame([dict(x) for x in data])
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# LEAVE MANAGEMENT
# ============================================================

def leave_page():
    st.title("🌴 Leave Management")

    employees = execute(
        "SELECT id, employee_code, first_name, last_name FROM employees WHERE status='Active'",
        fetch=True
    )

    if not employees:
        st.warning("No employees available.")
        return

    options = {
        f"{x['employee_code']} - {x['first_name']} {x['last_name'] or ''}": x["id"]
        for x in employees
    }

    selected = st.selectbox("Employee", list(options.keys()))
    employee_id = options[selected]

    with st.form("leave_form"):
        leave_type = st.selectbox("Leave Type", ["Annual Leave", "Sick Leave", "Casual Leave", "Emergency Leave"])
        c1, c2 = st.columns(2)
        start = c1.date_input("Start Date", date.today())
        end = c2.date_input("End Date", date.today())
        reason = st.text_area("Reason")

        submit = st.form_submit_button("Apply Leave")

        if submit:
            if end < start:
                st.error("End date cannot be before start date.")
            else:
                execute(
                    """
                    INSERT INTO leave_requests(
                        employee_id, leave_type, start_date, end_date, reason, applied_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (employee_id, leave_type, start.isoformat(), end.isoformat(), reason, datetime.now().isoformat())
                )
                st.success("Leave request submitted.")

    st.divider()

    data = execute(
        """
        SELECT
            l.id,
            e.employee_code AS Employee,
            e.first_name || ' ' || COALESCE(e.last_name,'') AS Name,
            l.leave_type AS Type,
            l.start_date AS Start,
            l.end_date AS End,
            l.reason AS Reason,
            l.status AS Status
        FROM leave_requests l
        JOIN employees e
        ON e.id=l.employee_id
        ORDER BY l.id DESC
        """,
        fetch=True
    )

    if data:
        df = pd.DataFrame([dict(x) for x in data])
        st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

        pending = [x for x in data if x["Status"] == "Pending"]
        if pending:
            st.subheader("Pending Requests")
            for request in pending:
                st.write(
                    f"**{request['Employee']}** | {request['Type']} | {request['Start']} → {request['End']}"
                )
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve", key=f"approve_{request['id']}"):
                    execute("UPDATE leave_requests SET status='Approved' WHERE id=?", (request["id"],))
                    st.rerun()
                if c2.button("❌ Reject", key=f"reject_{request['id']}"):
                    execute("UPDATE leave_requests SET status='Rejected' WHERE id=?", (request["id"],))
                    st.rerun()


# ============================================================
# PAYROLL
# ============================================================

def payroll_page():
    st.title("💰 Payroll Management")

    employees = execute(
        "SELECT id, employee_code, first_name, last_name, salary FROM employees WHERE status='Active'",
        fetch=True
    )

    if not employees:
        st.warning("No active employees.")
        return

    options = {
        f"{x['employee_code']} - {x['first_name']} {x['last_name'] or ''}": x
        for x in employees
    }

    selected = st.selectbox("Employee", list(options.keys()))
    emp = options[selected]

    month = st.text_input("Payroll Month", datetime.now().strftime("%Y-%m"))
    basic = st.number_input("Basic Salary", value=float(emp["salary"] or 0), min_value=0.0)
    allowance = st.number_input("Allowance", min_value=0.0)
    bonus = st.number_input("Bonus", min_value=0.0)
    overtime = st.number_input("Overtime", min_value=0.0)
    deduction = st.number_input("Deduction", min_value=0.0)

    net_salary = basic + allowance + bonus + overtime - deduction
    st.metric("Net Salary", f"{net_salary:,.2f}")

    if st.button("Generate Payroll"):
        execute(
            """
            INSERT INTO payroll(
                employee_id, month, basic_salary, allowance, bonus, deduction, overtime, net_salary, generated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                emp["id"], month, basic, allowance, bonus, deduction, overtime, net_salary, datetime.now().isoformat()
            )
        )
        st.success("Payroll generated successfully.")

    st.divider()

    data = execute(
        """
        SELECT
            p.month AS Month,
            e.employee_code AS Employee,
            e.first_name || ' ' || COALESCE(e.last_name,'') AS Name,
            p.net_salary AS Net_Salary,
            p.generated_at AS Generated_At
        FROM payroll p
        JOIN employees e ON e.id = p.employee_id
        ORDER BY p.id DESC
        """,
        fetch=True
    )

    if data:
        df = pd.DataFrame([dict(x) for x in data])
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# PLACEHOLDER PAGES (Tasks, Performance, Documents, Notifications, Audit Logs)
# ============================================================

def tasks_page():
    st.title("📋 Task Management")
    st.info("Task management module coming soon.")

def performance_page():
    st.title("⭐ Performance Review")
    st.info("Performance module coming soon.")

def documents_page():
    st.title("📁 Document Management")
    st.info("Document repository module coming soon.")

def notifications_page():
    st.title("🔔 Notifications")
    st.info("No new notifications.")

def audit_logs_page():
    st.title("📜 Audit Logs")
    data = execute("SELECT username, action, created_at FROM audit_logs ORDER BY id DESC LIMIT 100", fetch=True)
    if data:
        df = pd.DataFrame([dict(x) for x in data])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No audit logs found.")


# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

def main():
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        menu = sidebar()

        if menu == "Dashboard":
            dashboard()
        elif menu == "Employees":
            employees_page()
        elif menu == "Departments":
            departments_page()
        elif menu == "Attendance":
            attendance_page()
        elif menu == "Leave Management":
            leave_page()
        elif menu == "Payroll":
            payroll_page()
        elif menu == "Tasks":
            tasks_page()
        elif menu == "Performance":
            performance_page()
        elif menu == "Documents":
            documents_page()
        elif menu == "Notifications":
            notifications_page()
        elif menu == "Audit Logs":
            audit_logs_page()

if __name__ == "__main__":
    main()