"""
CPMS - College Project Management System
Tkinter + MySQL + Neon GUI + Simple Animations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import sys
import credentials as crds

# Cyberpunk theme
from cyberpunk_theme import (
    CYBER_BG,
    NEON_PINK,
    NEON_CYAN,
    NEON_GREEN,
    NEON_YELLOW,
    NEON_ORANGE,
    apply_cyberpunk_style,
    neon_label,
    neon_entry,
    neon_button,
)


# ==============================
#  DB CONFIG  (EDIT THIS)
# ==============================

DB_HOST = crds.DB_HOST
DB_USER = crds.DB_USER
DB_PASS = crds.DB_PASS
DB_NAME = crds.DB_NAME


# ==============================
#  UTILS
# ==============================

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest (same as your C code)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def show_text_window(title: str, content: str):
    """Open a simple window showing multi-line text (for reports, team details, etc.)."""
    win = tk.Toplevel()
    win.title(title)
    win.configure(bg=CYBER_BG)
    win.geometry("800x550")

    text = tk.Text(
        win,
        wrap="word",
        bg="#001124",
        fg=NEON_GREEN,
        insertbackground=NEON_GREEN,
        font=("Consolas", 11),
        relief="flat",
    )
    text.insert("1.0", content)
    text.config(state="disabled")
    text.pack(fill="both", expand=True, padx=10, pady=10)

    btn_close = neon_button(win, "CLOSE", win.destroy)
    btn_close.pack(pady=10)


class AnimatedHeaderMixin:
    def init_header(self, text: str):
        self.header_label = neon_label(self, text, NEON_PINK, size=20)
        self.header_label.pack(pady=15)
        self._fade_step = 0
        self.fade_header()

    def fade_header(self):
        # Two-color smooth fade
        colors = [NEON_PINK, NEON_CYAN]
        c1, c2 = colors[0], colors[1]

        # Step (0 → 100)
        t = (self._fade_step % 100) / 100.0

        # Linear interpolation between colors
        def lerp(a, b, t): return int(a + (b - a) * t)

        r = lerp(int(c1[1:3], 16), int(c2[1:3], 16), t)
        g = lerp(int(c1[3:5], 16), int(c2[3:5], 16), t)
        b = lerp(int(c1[5:7], 16), int(c2[5:7], 16), t)

        color = f"#{r:02x}{g:02x}{b:02x}"
        self.header_label.config(fg=color)

        self._fade_step += 1
        self.after(50, self.fade_header)



# ==============================
#  MAIN APP
# ==============================

class CPMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPMS - College Project Management System")
        self.geometry("1000x650")
        self.configure(bg=CYBER_BG)

        # Apply cyberpunk style to ttk widgets
        apply_cyberpunk_style(self)

        # DB connection
        self.conn = None
        self.connect_db()

        # User session
        self.current_role = None  # "team", "mentor", "evaluator"
        self.current_user_id = None
        self.current_user_name = None  # mentors store name, others store ID

        # Evaluator queue (list of dicts)
        self.eval_queue = []

        # Container frame (for swapping screens)
        self.container = tk.Frame(self, bg=CYBER_BG)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginFrame, TeamFrame, MentorFrame, EvaluatorFrame, ReportsFrame):
            frame = F(parent=self.container, app=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    # ---------------------- DB CONNECTION ----------------------

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
            )
            if self.conn.is_connected():
                print("Connected to MySQL database.")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to MySQL:\n{e}")
            sys.exit(1)

    def run_query(self, query, params=None, fetchone=False, fetchall=False):
        """Helper for executing queries safely."""
        if self.conn is None or not self.conn.is_connected():
            self.connect_db()

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params or ())
            if fetchone:
                row = cursor.fetchone()
                cursor.close()
                return row
            if fetchall:
                rows = cursor.fetchall()
                cursor.close()
                return rows
            self.conn.commit()
            cursor.close()
            return None
        except Error as e:
            cursor.close()
            messagebox.showerror("MySQL Error", f"Error executing query:\n{e}")
            return None

    # ---------------------- FRAME MANAGEMENT ----------------------

    def show_frame(self, frame_cls):
        frame = self.frames[frame_cls]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # ---------------------- AUTH / LOGIN ----------------------

    def login(self, user_id: str, password: str, status_label: str):
        """
        status_label: "Team", "Mentor", "Evaluator" (from combobox)
        DB 'status' values: "team", "mentor", "evaluator"
        """
        role_map = {
            "Team": "team",
            "Mentor": "mentor",
            "Evaluator": "evaluator",
        }
        status = role_map.get(status_label)
        if status is None:
            messagebox.showerror("Login Error", "Invalid role selected.")
            return False

        hashed = hash_password(password)

        row = self.run_query(
            "SELECT name FROM users WHERE id=%s AND password=%s AND status=%s;",
            (user_id, hashed, status),
            fetchone=True,
        )

        if not row:
            messagebox.showerror("Login Failed", "Invalid ID or password or status.")
            return False

        self.current_role = status
        if status == "mentor":
            self.current_user_name = row[0]
        else:
            self.current_user_name = user_id
        self.current_user_id = user_id

        # Go to appropriate dashboard
        if status == "team":
            self.show_frame(TeamFrame)
        elif status == "mentor":
            self.show_frame(MentorFrame)
        else:
            self.show_frame(EvaluatorFrame)
        return True

    # ==============================
    # TEAM FUNCTIONS
    # ==============================

    def team_input_proposals(self, team_id: str):
        proposals = []
        for i in range(1, 6):
            p = simpledialog.askstring(
                "Input Proposal",
                f"Proposal {i} for team {team_id}:",
                parent=self,
            )
            if p is None:
                p = ""  # allow cancel as empty
            proposals.append(p)

        q = (
            "UPDATE team_detail "
            "SET proposal1=%s, proposal2=%s, proposal3=%s, proposal4=%s, proposal5=%s "
            "WHERE team_id=%s"
        )
        self.run_query(q, (*proposals, team_id))
        messagebox.showinfo("Success", "Proposals updated successfully.")

    def team_submit_project_url(self, team_id: str):
        url = simpledialog.askstring(
            "Submit Project URL",
            f"Enter project URL for team {team_id}:",
            parent=self,
        )
        if not url:
            return

        now = datetime.now()
        submission_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Fetch deadline
        row = self.run_query(
            "SELECT submission_deadline FROM team_detail WHERE team_id=%s;",
            (team_id,),
            fetchone=True,
        )

        deadline_str = None
        is_late = 0
        if row and row[0]:
            # row[0] can be datetime or string depending on connector
            if isinstance(row[0], datetime):
                deadline_dt = row[0]
            else:
                deadline_dt = datetime.strptime(str(row[0]), "%Y-%m-%d %H:%M:%S")
            deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")
            is_late = 1 if now > deadline_dt else 0
        else:
            deadline_str = None  # treat as no deadline

        # Update
        q = (
            "UPDATE team_detail "
            "SET project_url=%s, submission_time=%s, is_late=%s "
            "WHERE team_id=%s"
        )
        self.run_query(q, (url, submission_time_str, is_late, team_id))

        msg = f"Project submitted at {submission_time_str}.\n"
        if deadline_str:
            msg += f"Deadline was: {deadline_str}\n"
            msg += "Status: LATE" if is_late else "Status: ON TIME"
        else:
            msg += "No deadline configured. Treated as ON TIME."
        messagebox.showinfo("Submission", msg)

    def team_view_selected_proposal(self, team_id: str):
        row = self.run_query(
            "SELECT selected_proposal, is_selected FROM team_detail WHERE team_id=%s;",
            (team_id,),
            fetchone=True,
        )
        if not row:
            messagebox.showwarning("Not Found", f"No team found with ID {team_id}.")
            return
        selected_proposal, is_selected = row
        if is_selected and selected_proposal:
            show_text_window(
                "Selected Proposal",
                f"Team ID: {team_id}\n\nSelected Proposal:\n{selected_proposal}",
            )
        else:
            messagebox.showinfo(
                "Not Selected",
                f"No proposal has been selected yet for Team ID {team_id}.",
            )

    def team_view_marks(self, team_id: str):
        row = self.run_query(
            "SELECT marks FROM team_detail WHERE team_id=%s;",
            (team_id,),
            fetchone=True,
        )
        if not row or row[0] is None:
            messagebox.showinfo(
                "Marks",
                f"No marks available yet for Team ID {team_id}.",
            )
        else:
            messagebox.showinfo("Marks", f"Team {team_id} marks: {row[0]}")

    def team_show_details(self, team_id: str):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM team_detail WHERE team_id=%s;", (team_id,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        finally:
            cursor.close()

        if not rows:
            messagebox.showwarning("No data", f"No details found for team {team_id}.")
            return

        content = [f"Team ID: {team_id}\n" + "-" * 40]
        for row in rows:
            for col_name, value in zip(columns, row):
                content.append(f"{col_name}: {value if value is not None else 'NULL'}")
            content.append("-" * 40)

        show_text_window("Team Details", "\n".join(content))

    # ==============================
    # MENTOR FUNCTIONS
    # ==============================

    def mentor_check_team(self, team_id: str, mentor_name: str) -> bool:
        row = self.run_query(
            "SELECT COUNT(*) FROM team_detail "
            "WHERE team_id=%s AND mentor=%s;",
            (team_id, mentor_name),
            fetchone=True,
        )
        if not row or row[0] == 0:
            messagebox.showerror(
                "Access Denied",
                f"'{mentor_name}' is NOT mentor of Team '{team_id}'.",
            )
            return False
        return True

    def mentor_select_proposal(self, mentor_name: str):
        team_id = simpledialog.askstring(
            "Select Proposal", "Team ID:", parent=self
        )
        if not team_id:
            return

        if not self.mentor_check_team(team_id, mentor_name):
            return

        num = simpledialog.askinteger(
            "Select Proposal",
            "Proposal number (1-5):",
            minvalue=1,
            maxvalue=5,
            parent=self,
        )
        if not num:
            return

        proposal_col = f"proposal{num}"
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                f"SELECT {proposal_col} FROM team_detail WHERE team_id=%s;",
                (team_id,),
            )
            row = cursor.fetchone()
        finally:
            cursor.close()

        if not row or not row[0]:
            messagebox.showwarning(
                "Empty Proposal", f"Proposal {num} is empty or not found."
            )
            return

        selected_proposal = row[0]
        self.run_query(
            "UPDATE team_detail "
            "SET is_selected=1, selected_proposal=%s "
            "WHERE team_id=%s;",
            (selected_proposal, team_id),
        )
        messagebox.showinfo(
            "Success",
            f"Proposal {num} selected successfully for Team {team_id}!",
        )

    def mentor_reject_all(self, mentor_name: str):
        team_id = simpledialog.askstring(
            "Reject All Proposals", "Team ID:", parent=self
        )
        if not team_id:
            return

        if not self.mentor_check_team(team_id, mentor_name):
            return

        self.run_query(
            "UPDATE team_detail SET is_selected=0, selected_proposal=NULL "
            "WHERE team_id=%s;",
            (team_id,),
        )
        messagebox.showinfo(
            "Success",
            f"All proposals rejected for Team {team_id}.",
        )

    def mentor_show_team_details(self, mentor_name: str):
        team_id = simpledialog.askstring(
            "Team Details (Mentor View)", "Team ID:", parent=self
        )
        if not team_id:
            return

        if not self.mentor_check_team(team_id, mentor_name):
            return

        self.team_show_details(team_id)

    # ==============================
    # EVALUATOR FUNCTIONS
    # ==============================

    def evaluator_extract_projects(self, evaluator_id: str):
        sem = simpledialog.askinteger(
            "Extract Projects", "Semester:", minvalue=1, maxvalue=20, parent=self
        )
        if sem is None:
            return

        # clear queue
        self.eval_queue = []

        query = (
            "SELECT semester, team_id, team_name, IFNULL(is_late,0), "
            "IFNULL(project_url,'N/A') "
            "FROM team_detail "
            "WHERE semester=%s "
            "AND LOWER(TRIM(evaluator)) = LOWER(TRIM((SELECT name FROM users WHERE id=%s))) "
            "AND (marks IS NULL OR marks=0) "
            "ORDER BY IFNULL(submission_time, NOW()) ASC;"
        )
        rows = self.run_query(query, (sem, evaluator_id), fetchall=True) or []

        for row in rows:
            sem_, team_id, team_name, is_late, project_url = row
            self.eval_queue.append(
                {
                    "semester": sem_,
                    "team_id": team_id,
                    "team_name": team_name,
                    "is_late": bool(is_late),
                    "project_url": project_url,
                }
            )

        if self.eval_queue:
            messagebox.showinfo(
                "Extracted",
                f"{len(self.eval_queue)} project(s) extracted for semester {sem}.",
            )
        else:
            messagebox.showinfo(
                "Empty",
                "No pending projects found for this semester.",
            )

    def evaluator_view_queue(self):
        if not self.eval_queue:
            messagebox.showinfo(
                "Queue Empty", "No projects currently extracted. Extract first."
            )
            return

        lines = [
            "Semester   Team ID     Team Name                Late?   Project URL",
            "-" * 75,
        ]
        for p in self.eval_queue:
            lines.append(
                f"{p['semester']:<10} {p['team_id']:<10} {p['team_name']:<20} "
                f"{'YES' if p['is_late'] else 'NO':<7} {p['project_url']}"
            )
        show_text_window("Extracted Project Queue", "\n".join(lines))

    def evaluator_evaluate(self):
        if not self.eval_queue:
            messagebox.showinfo(
                "No Projects", "No projects in queue. Extract projects first."
            )
            return

        evaluated_count = 0
        while self.eval_queue:
            p = self.eval_queue.pop(0)

            info = (
                f"Semester: {p['semester']}\n"
                f"Team ID: {p['team_id']}\n"
                f"Team Name: {p['team_name']}\n"
                f"Late Status: {'LATE' if p['is_late'] else 'ON TIME'}\n"
                f"Project URL: {p['project_url']}\n"
            )

            marks = simpledialog.askinteger(
                "Evaluate Project",
                info + "\nEnter marks (0-100):",
                minvalue=0,
                maxvalue=100,
                parent=self,
            )
            if marks is None:
                # user cancelled; push project back and break
                self.eval_queue.insert(0, p)
                break

            self.run_query(
                "UPDATE team_detail SET marks=%s WHERE team_id=%s;",
                (marks, p["team_id"]),
            )
            evaluated_count += 1

            if self.eval_queue:
                cont = messagebox.askyesno(
                    "Continue?",
                    f"Marks ({marks}/100) saved for {p['team_id']}.\n\n"
                    "Evaluate next project?",
                )
                if not cont:
                    break
            else:
                messagebox.showinfo(
                    "Done",
                    f"Marks ({marks}/100) saved for {p['team_id']}.\n\n"
                    f"All projects in queue evaluated.\nTotal evaluated: {evaluated_count}",
                )
        if evaluated_count > 0 and self.eval_queue:
            messagebox.showinfo(
                "Paused",
                f"Evaluation paused. {evaluated_count} project(s) evaluated.\n"
                f"Remaining in queue: {len(self.eval_queue)}",
            )

    def evaluator_set_deadline(self):
        deadline_str = simpledialog.askstring(
            "Set Global Deadline",
            "New deadline (YYYY-MM-DD HH:MM:SS):",
            parent=self,
        )
        if not deadline_str:
            return

        try:
            _ = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(
                "Format Error", "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS."
            )
            return

        q = (
            "UPDATE team_detail SET submission_deadline=%s "
            "WHERE project_url IS NULL;"
        )
        self.run_query(q, (deadline_str,))
        messagebox.showinfo(
            "Deadline Set",
            f"Global deadline set to: {deadline_str}\n"
            "(Rows with NULL project_url updated.)",
        )

    def evaluator_show_deadline(self):
        row = self.run_query(
            "SELECT submission_deadline FROM team_detail "
            "WHERE submission_deadline IS NOT NULL "
            "ORDER BY submission_deadline DESC LIMIT 1;",
            fetchone=True,
        )
        if not row or not row[0]:
            messagebox.showinfo(
                "No Deadline", "No global submission deadline is set yet."
            )
        else:
            messagebox.showinfo(
                "Current Deadline", f"Current Global Deadline:\n{row[0]}"
            )

    # ==============================
    # REPORTS
    # ==============================

    def report_semester(self):
        sem = simpledialog.askinteger(
            "Semester Report", "Semester:", minvalue=1, maxvalue=20, parent=self
        )
        if sem is None:
            return

        q = (
            "SELECT semester, subject, mentor, team_id, team_name, marks "
            "FROM team_detail "
            "WHERE project_url IS NOT NULL AND marks IS NOT NULL AND semester=%s;"
        )
        rows = self.run_query(q, (sem,), fetchall=True) or []

        if not rows:
            messagebox.showinfo(
                "No Data",
                f"No teams found for semester {sem} with completed submissions and marks.",
            )
            return

        # Sort by marks desc
        rows.sort(key=lambda r: r[5], reverse=True)

        lines = [f"SEMESTER {sem} – RANKED TEAMS", "-" * 50]
        for i, (sem_, subject, mentor, team_id, team_name, marks) in enumerate(rows):
            lines.append(
                f"{i+1:2d}. {team_id} ({team_name}) — {marks} marks"
            )

        marks_list = [r[5] for r in rows]
        highest = marks_list[0]
        lowest = marks_list[-1]
        avg = sum(marks_list) / len(marks_list)

        lines.append("-" * 50)
        lines.append(f"Total Teams : {len(rows)}")
        lines.append(f"Highest     : {highest} ({rows[0][3]})")
        lines.append(f"Lowest      : {lowest} ({rows[-1][3]})")
        lines.append(f"Average     : {avg:.2f}")

        show_text_window("Semester Report", "\n".join(lines))

    def report_mentor(self):
        mentor = simpledialog.askstring(
            "Mentor Report", "Mentor name:", parent=self
        )
        if not mentor:
            return

        q = (
            "SELECT semester, subject, mentor, team_id, team_name, marks "
            "FROM team_detail "
            "WHERE project_url IS NOT NULL AND marks IS NOT NULL "
            "AND LOWER(mentor)=LOWER(%s);"
        )
        rows = self.run_query(q, (mentor,), fetchall=True) or []

        if not rows:
            messagebox.showinfo(
                "No Data",
                f"No teams found for mentor {mentor} with completed submissions and marks.",
            )
            return

        rows.sort(key=lambda r: r[5], reverse=True)

        lines = [f"MENTOR REPORT – {mentor}", "-" * 50]
        for i, (sem, subject, mentor_, team_id, team_name, marks) in enumerate(rows):
            lines.append(
                f"{i+1:2d}. {team_id} ({team_name}) — {marks} marks"
            )

        marks_list = [r[5] for r in rows]
        highest = marks_list[0]
        lowest = marks_list[-1]
        avg = sum(marks_list) / len(marks_list)

        lines.append("-" * 50)
        lines.append(f"Total Teams : {len(rows)}")
        lines.append(f"Highest     : {highest} ({rows[0][3]})")
        lines.append(f"Lowest      : {lowest} ({rows[-1][3]})")
        lines.append(f"Average     : {avg:.2f}")

        show_text_window("Mentor Report", "\n".join(lines))

    def report_subject(self):
        subject = simpledialog.askstring(
            "Subject Report", "Subject:", parent=self
        )
        if not subject:
            return

        q = (
            "SELECT semester, subject, mentor, team_id, team_name, marks "
            "FROM team_detail "
            "WHERE project_url IS NOT NULL AND marks IS NOT NULL "
            "AND LOWER(subject)=LOWER(%s);"
        )
        rows = self.run_query(q, (subject,), fetchall=True) or []

        if not rows:
            messagebox.showinfo(
                "No Data",
                f"No teams found for subject {subject} with completed submissions and marks.",
            )
            return

        rows.sort(key=lambda r: r[5], reverse=True)

        lines = [f"SUBJECT REPORT – {subject}", "-" * 50]
        for i, (sem, subject_, mentor, team_id, team_name, marks) in enumerate(rows):
            lines.append(
                f"{i+1:2d}. {team_id} ({team_name}) — {marks} marks"
            )

        marks_list = [r[5] for r in rows]
        highest = marks_list[0]
        lowest = marks_list[-1]
        avg = sum(marks_list) / len(marks_list)

        lines.append("-" * 50)
        lines.append(f"Total Teams : {len(rows)}")
        lines.append(f"Highest     : {highest} ({rows[0][3]})")
        lines.append(f"Lowest      : {lowest} ({rows[-1][3]})")
        lines.append(f"Average     : {avg:.2f}")

        show_text_window("Subject Report", "\n".join(lines))

    def report_leaderboard(self):
        q = (
            "SELECT semester, subject, mentor, team_id, team_name, marks "
            "FROM team_detail "
            "WHERE project_url IS NOT NULL AND marks IS NOT NULL;"
        )
        rows = self.run_query(q, fetchall=True) or []

        if not rows:
            messagebox.showinfo(
                "No Data",
                "No team data available (no completed submissions with marks).",
            )
            return

        rows.sort(key=lambda r: r[5], reverse=True)

        lines = ["GLOBAL LEADERBOARD", "-" * 50]
        for i, (sem, subject, mentor, team_id, team_name, marks) in enumerate(rows):
            lines.append(
                f"{i+1:2d}. {team_id} ({team_name}, Sem {sem}) — {marks} marks"
            )

        show_text_window("Leaderboard", "\n".join(lines))

    def report_view_team_by_id(self):
        team_id = simpledialog.askstring(
            "View Team by ID", "Team ID (e.g., T1001):", parent=self
        )
        if not team_id:
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT semester, subject, team_id, team_name, "
                "proposal1, proposal2, proposal3, proposal4, proposal5, "
                "project_url, IFNULL(marks, 'Not Given') "
                "FROM team_detail WHERE team_id=%s;",
                (team_id,),
            )
            row = cursor.fetchone()
        finally:
            cursor.close()

        if not row:
            messagebox.showinfo(
                "Not Found",
                f"Team details not found for ID {team_id}.",
            )
            return

        (
            sem,
            subject,
            team_id_db,
            team_name,
            p1,
            p2,
            p3,
            p4,
            p5,
            project_url,
            marks,
        ) = row

        lines = [
            "TEAM DETAILS",
            "-" * 50,
            f"Team ID        : {team_id_db}",
            f"Team Name      : {team_name}",
            f"Semester       : {sem}",
            f"Subject        : {subject}",
            "-" * 50,
            f"Proposal 1     : {p1}",
            f"Proposal 2     : {p2}",
            f"Proposal 3     : {p3}",
            f"Proposal 4     : {p4}",
            f"Proposal 5     : {p5}",
            "-" * 50,
            f"Project URL    : {project_url or 'Not Submitted'}",
            f"Marks Obtained : {marks}",
        ]

        show_text_window("Team Details", "\n".join(lines))


# ==============================
#   TKINTER FRAMES (CYBERPUNK)
# ==============================

class LoginFrame(tk.Frame, AnimatedHeaderMixin):
    def __init__(self, parent, app: CPMSApp):
        tk.Frame.__init__(self, parent, bg=CYBER_BG)
        self.app = app

        self.init_header("CPMS // COLLEGE PROJECT MANAGEMENT SYSTEM")

        # Subtle moving underline animation
        self.underline = tk.Label(self, text="=" * 45, fg=NEON_CYAN, bg=CYBER_BG, font=("Consolas", 10))
        self.underline.pack()

        form = tk.Frame(self, bg=CYBER_BG)
        form.pack(pady=30)

        neon_label(form, "USER ID:", NEON_CYAN, 13).grid(row=0, column=0, sticky="e", padx=10, pady=8)
        self.entry_user = neon_entry(form, width=28)
        self.entry_user.grid(row=0, column=1, padx=10, pady=8)

        neon_label(form, "PASSWORD:", NEON_CYAN, 13).grid(row=1, column=0, sticky="e", padx=10, pady=8)
        self.entry_pass = neon_entry(form, width=28)
        self.entry_pass.config(show="●")
        self.entry_pass.grid(row=1, column=1, padx=10, pady=8)

        neon_label(form, "ROLE:", NEON_CYAN, 13).grid(row=2, column=0, sticky="e", padx=10, pady=8)
        self.combo_role = ttk.Combobox(form, values=["Team", "Mentor", "Evaluator"], state="readonly", width=25)
        self.combo_role.current(0)
        self.combo_role.grid(row=2, column=1, padx=10, pady=8)

        btn_row = tk.Frame(self, bg=CYBER_BG)
        btn_row.pack(pady=15)

        neon_button(btn_row, "LOGIN", self.do_login).grid(row=0, column=0, padx=8)
        # Public reports accessible ONLY here (not in dashboards)
        neon_button(btn_row, "PUBLIC REPORTS (NO LOGIN)",
                    lambda: self.app.show_frame(ReportsFrame)).grid(row=0, column=1, padx=8)

        self.message_label = neon_label(self, "", NEON_ORANGE, 11)
        self.message_label.pack(pady=5)

    def do_login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get()
        role = self.combo_role.get()
        if not user or not pwd:
            self.message_label.config(text="ENTER USER ID + PASSWORD", fg=NEON_ORANGE)
            return
        ok = self.app.login(user, pwd, role)
        if not ok:
            self.message_label.config(text="LOGIN FAILED – CHECK CREDENTIALS", fg=NEON_ORANGE)


class TeamFrame(tk.Frame, AnimatedHeaderMixin):
    def __init__(self, parent, app: CPMSApp):
        tk.Frame.__init__(self, parent, bg=CYBER_BG)
        self.app = app

        self.init_header("TEAM DASHBOARD // NEON TERMINAL")

        self.label_info = neon_label(self, "", NEON_GREEN, 12)
        self.label_info.pack(pady=5)

        btn_frame = tk.Frame(self, bg=CYBER_BG)
        btn_frame.pack(pady=25)

        neon_button(btn_frame, "INPUT PROPOSALS", self.do_input_proposals).grid(row=0, column=0, padx=10, pady=8)
        neon_button(btn_frame, "SUBMIT PROJECT URL", self.do_submit_url).grid(row=0, column=1, padx=10, pady=8)
        neon_button(btn_frame, "VIEW SELECTED PROPOSAL", self.do_view_selected).grid(row=1, column=0, padx=10, pady=8)
        neon_button(btn_frame, "SHOW TEAM DETAILS", self.do_show_details).grid(row=1, column=1, padx=10, pady=8)
        neon_button(btn_frame, "VIEW MARKS", self.do_view_marks).grid(row=2, column=0, padx=10, pady=8)

        # NOTE: Public Reports Menu button REMOVED here as requested

        neon_button(self, "LOGOUT", lambda: self.app.show_frame(LoginFrame)).pack(pady=20)

    def on_show(self):
        team_id = self.app.current_user_id
        self.label_info.config(text=f"LOGGED IN AS TEAM: {team_id}")

    def do_input_proposals(self):
        self.app.team_input_proposals(self.app.current_user_id)

    def do_submit_url(self):
        self.app.team_submit_project_url(self.app.current_user_id)

    def do_view_selected(self):
        self.app.team_view_selected_proposal(self.app.current_user_id)

    def do_show_details(self):
        self.app.team_show_details(self.app.current_user_id)

    def do_view_marks(self):
        self.app.team_view_marks(self.app.current_user_id)


class MentorFrame(tk.Frame, AnimatedHeaderMixin):
    def __init__(self, parent, app: CPMSApp):
        tk.Frame.__init__(self, parent, bg=CYBER_BG)
        self.app = app

        self.init_header("MENTOR DASHBOARD // CONTROL NODE")

        self.label_info = neon_label(self, "", NEON_GREEN, 12)
        self.label_info.pack(pady=5)

        btn_frame = tk.Frame(self, bg=CYBER_BG)
        btn_frame.pack(pady=25)

        neon_button(btn_frame, "SELECT PROPOSAL", self.do_select_proposal).grid(row=0, column=0, padx=10, pady=8)
        neon_button(btn_frame, "REJECT ALL PROPOSALS", self.do_reject_all).grid(row=0, column=1, padx=10, pady=8)
        neon_button(btn_frame, "SHOW TEAM DETAILS", self.do_show_team_details).grid(row=1, column=0, padx=10, pady=8)

        # NOTE: Public Reports Menu button REMOVED here as requested

        neon_button(self, "LOGOUT", lambda: self.app.show_frame(LoginFrame)).pack(pady=20)

    def on_show(self):
        self.label_info.config(text=f"LOGGED IN AS MENTOR: {self.app.current_user_name}")

    def do_select_proposal(self):
        self.app.mentor_select_proposal(self.app.current_user_name)

    def do_reject_all(self):
        self.app.mentor_reject_all(self.app.current_user_name)

    def do_show_team_details(self):
        self.app.mentor_show_team_details(self.app.current_user_name)


class EvaluatorFrame(tk.Frame, AnimatedHeaderMixin):
    def __init__(self, parent, app: CPMSApp):
        tk.Frame.__init__(self, parent, bg=CYBER_BG)
        self.app = app

        self.init_header("EVALUATOR DASHBOARD // JUDGE CORE")

        self.label_info = neon_label(self, "", NEON_GREEN, 12)
        self.label_info.pack(pady=5)

        btn_frame = tk.Frame(self, bg=CYBER_BG)
        btn_frame.pack(pady=25)

        neon_button(btn_frame, "EXTRACT PROJECTS BY SEMESTER", self.do_extract).grid(row=0, column=0, padx=10, pady=8)
        neon_button(btn_frame, "VIEW EXTRACTED LIST", self.do_view_list).grid(row=0, column=1, padx=10, pady=8)
        neon_button(btn_frame, "EVALUATE BY SEMESTER", self.do_evaluate).grid(row=1, column=0, padx=10, pady=8)
        neon_button(btn_frame, "SET GLOBAL SUBMISSION DEADLINE", self.do_set_deadline).grid(row=1, column=1, padx=10, pady=8)
        neon_button(btn_frame, "SHOW CURRENT GLOBAL DEADLINE", self.do_show_deadline).grid(row=2, column=0, padx=10, pady=8)

        # NOTE: Public Reports Menu button REMOVED here as requested

        neon_button(self, "LOGOUT", lambda: self.app.show_frame(LoginFrame)).pack(pady=20)

    def on_show(self):
        self.label_info.config(text=f"LOGGED IN AS EVALUATOR: {self.app.current_user_id}")

    def do_extract(self):
        self.app.evaluator_extract_projects(self.app.current_user_id)

    def do_view_list(self):
        self.app.evaluator_view_queue()

    def do_evaluate(self):
        self.app.evaluator_evaluate()

    def do_set_deadline(self):
        self.app.evaluator_set_deadline()

    def do_show_deadline(self):
        self.app.evaluator_show_deadline()


class ReportsFrame(tk.Frame, AnimatedHeaderMixin):
    def __init__(self, parent, app: CPMSApp):
        tk.Frame.__init__(self, parent, bg=CYBER_BG)
        self.app = app

        self.init_header("PUBLIC ANALYTICS // REPORTS HUB")

        btn_frame = tk.Frame(self, bg=CYBER_BG)
        btn_frame.pack(pady=20)

        neon_button(btn_frame, "SEMESTER-WISE REPORT", app.report_semester).grid(row=0, column=0, padx=10, pady=8)
        neon_button(btn_frame, "MENTOR-WISE REPORT", app.report_mentor).grid(row=0, column=1, padx=10, pady=8)
        neon_button(btn_frame, "SUBJECT-WISE REPORT", app.report_subject).grid(row=1, column=0, padx=10, pady=8)
        neon_button(btn_frame, "GLOBAL LEADERBOARD", app.report_leaderboard).grid(row=1, column=1, padx=10, pady=8)
        neon_button(btn_frame, "VIEW TEAM DETAILS BY ID", app.report_view_team_by_id).grid(row=2, column=0, padx=10, pady=8)

        neon_button(self, "BACK TO LOGIN / MAIN", lambda: app.show_frame(LoginFrame)).pack(pady=25)

    def on_show(self):
        # Could add some extra animation or status later
        pass


# ==============================
#  MAIN
# ==============================

if __name__ == "__main__":
    app = CPMSApp()
    app.mainloop()
