# CPMS --- College Project Management System

A desktop-based College Project Management System built with **Python**,
**Tkinter**, and **MySQL**. The interface uses a cyberpunk-inspired neon
theme.

## Features

### Team

-   Sign in using a team ID and password.
-   Submit up to five project proposals.
-   Submit a project URL.
-   View the selected proposal and team details.
-   Check marks when they are available.

### Mentor

-   Sign in as a mentor.
-   View details for teams assigned to the mentor.
-   Select one of a team's submitted proposals.
-   Reject all proposals for a team.

### Evaluator

-   Sign in as an evaluator.
-   Extract pending projects by semester.
-   View the extracted evaluation queue.
-   Assign marks to submitted projects.
-   Set and view submission deadlines.

### Reports

-   View semester-wise, mentor-wise, and subject-wise reports.
-   View the global leaderboard.
-   Look up a team by ID.

## Technology Stack

-   **Python 3.13** --- application logic
-   **Tkinter / ttk** --- desktop GUI
-   **MySQL Server** --- persistent data storage
-   **mysql-connector-python** --- Python-to-MySQL connectivity

## Project Structure

The project folder used during setup was `CPMS/pbl_ds_python`.

``` text
CPMS/
└── pbl_ds_python/
    ├── cpms_tk.py
    ├── app.py
    ├── auth.py
    ├── credentials.py
    ├── cyberpunk_theme.py
    ├── database.py
    └── screens/                 # used by the modular app.py version
        ├── login_screen.py
        ├── team_screen.py
        ├── mentor_screen.py
        └── evaluator_screen.py
```

Your local folder may contain additional files. Keep each version's
supporting files together with its entry-point file.

## Requirements

1.  Python 3.13 (or another compatible Python 3 version)
2.  MySQL Server installed and running
3.  VS Code (optional, but useful for editing and running the project)
4.  The Python package `mysql-connector-python`

Tkinter is normally included with Python on Windows.

## Setup

### 1. Open the project folder

Open `CPMS/pbl_ds_python` in VS Code.

### 2. Open the VS Code terminal

Select **Terminal → New Terminal**. Confirm the terminal is in the
`pbl_ds_python` directory.

If necessary, run this in PowerShell (adjust the path if your project is
stored elsewhere):

``` powershell
cd C:\Users\hp\OneDrive\Desktop\CPMS\pbl_ds_python
```

### 3. Check Python

``` powershell
python --version
```

### 4. Install the MySQL connector

``` powershell
python -m pip install mysql-connector-python
```

### 5. Configure database credentials

Open `credentials.py`. It should define these values:

``` python
DB_HOST = "127.0.0.1"
DB_USER = "your_mysql_username"
DB_PASS = "your_mysql_password"
DB_NAME = "team_management"
```

Use the username and password configured for your own MySQL server. Do
not commit real passwords to a public repository. Consider keeping
secrets in environment variables or a local, untracked configuration
file.

### 6. Prepare the database

The application expects a MySQL database named `team_management`. The
database must contain the tables and columns used by the application,
including `users` and the team/project table.

The current local database was confirmed to contain these tables:

-   `users`
-   `team_details`
-   `project_deadline`

**Important schema mismatch:** the `cpms_tk.py` code currently contains
SQL statements that refer to `team_detail` (singular), while the
database table found during setup is named `team_details` (plural). This
can cause errors such as:

``` text
Table 'team_management.team_detail' doesn't exist
```

Before using team, mentor, evaluator, or reporting features, update the
relevant SQL references in the code to match the actual schema, or
deliberately migrate the schema after taking a backup. Do not blindly
rename every occurrence: inspect SQL table references and make sure the
table and column names match. The complete database schema and seed data
were not included in the files reviewed here, so this README does not
invent SQL to create them.

## Run the Project

### Main CPMS application

From the `pbl_ds_python` directory, run:

``` powershell
python cpms_tk.py
```

This starts the Tkinter desktop application.

### Modular application (alternative)

The separate `app.py` entry point imports modules from a `screens`
package. Run it only if the required `screens` folder and all its
imported files are present:

``` powershell
python app.py
```

Do not run both entry points at the same time.

## Verify the Database Connection

From the `pbl_ds_python` directory, run:

``` powershell
python -c "import mysql.connector; from credentials import DB_HOST, DB_USER, DB_PASS, DB_NAME; c=mysql.connector.connect(host=DB_HOST,user=DB_USER,password=DB_PASS,database=DB_NAME); print('DATABASE CONNECTED SUCCESSFULLY'); c.close()"
```

If successful, the terminal prints:

``` text
DATABASE CONNECTED SUCCESSFULLY
```

This verifies connectivity and database access, but does not verify that
all required tables, columns, or login records exist.

To list the existing tables:

``` powershell
python -c "from database import fetch_all; print(fetch_all('SHOW TABLES'))"
```

## Troubleshooting

  --------------------------------------------------------------------------------------------------------
  Error or symptom                                       What to check
  ------------------------------------------------------ -------------------------------------------------
  `can't open file ... cpms_tk.py`                       Make sure the terminal is in `pbl_ds_python`,
                                                         where the file is located.

  `ModuleNotFoundError: No module named 'mysql'`         Run
                                                         `python -m pip install mysql-connector-python`.

  `ModuleNotFoundError: No module named 'credentials'`   Run the command from the folder containing
                                                         `credentials.py`.

  `Access denied for user`                               Check `DB_USER` and `DB_PASS` in `credentials.py`
                                                         and your MySQL permissions.

  `Unknown database 'team_management'`                   Create or select the correct database and confirm
                                                         the name in `credentials.py`.

  `Can't connect to MySQL server`                        Confirm the MySQL Server service is running and
                                                         `DB_HOST` is correct.

  `Table 'team_management.team_detail' doesn't exist`    The code uses `team_detail`, but the observed
                                                         table is `team_details`; reconcile the SQL
                                                         references and schema.

  `LOGIN FAILED – CHECK CREDENTIALS`                     Check that the user ID, password, and selected
                                                         role match a record in `users`. Confirm password
                                                         hashing matches the code before changing stored
                                                         values.
  --------------------------------------------------------------------------------------------------------

## Security Notes

-   Do not publish `credentials.py` with a real database password.
-   Do not share database passwords in screenshots or chat.
-   Back up the database before modifying tables or schema.
-   Use test accounts while validating the application.

## Current Setup Status

During local testing, the Python application opened, and a direct MySQL
connection test succeeded. A later feature action failed because the
code queried `team_detail`, while the database contained `team_details`.
Login and all role-specific workflows should be tested again after
resolving the schema mismatch and verifying the required user records.

------------------------------------------------------------------------
