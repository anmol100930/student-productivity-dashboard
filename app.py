import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Student Productivity & Placement Dashboard",
    layout="wide"
)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
conn = sqlite3.connect("productivity.db", check_same_thread=False)
c = conn.cursor()

# -----------------------------
# CREATE TABLES
# -----------------------------
c.execute("""
CREATE TABLE IF NOT EXISTS productivity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT,
    study_hours REAL,
    distraction_hours REAL,
    main_distraction TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS dsa_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT,
    topic TEXT,
    questions_solved INTEGER,
    difficulty TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    role TEXT,
    status TEXT,
    applied_date TEXT
)
""")

conn.commit()

# -----------------------------
# APP TITLE
# -----------------------------
st.title("📊 Student Productivity & Placement Analytics Dashboard")
st.write(
    "Track study hours, distractions, DSA preparation, and internship applications "
    "in one dashboard."
)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Productivity Entry",
        "Add DSA Progress",
        "Add Internship Application",
        "View Data"
    ]
)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def load_productivity_data():
    return pd.read_sql_query("SELECT * FROM productivity", conn)

def load_dsa_data():
    return pd.read_sql_query("SELECT * FROM dsa_progress", conn)

def load_application_data():
    return pd.read_sql_query("SELECT * FROM applications", conn)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
if menu == "Dashboard":
    st.header("Overall Dashboard")

    productivity_df = load_productivity_data()
    dsa_df = load_dsa_data()
    app_df = load_application_data()

    total_study = productivity_df["study_hours"].sum() if not productivity_df.empty else 0
    total_distraction = productivity_df["distraction_hours"].sum() if not productivity_df.empty else 0
    total_questions = dsa_df["questions_solved"].sum() if not dsa_df.empty else 0
    total_apps = len(app_df) if not app_df.empty else 0

    if total_study + total_distraction > 0:
        productivity_score = round(
            (total_study / (total_study + total_distraction)) * 100, 2
        )
    else:
        productivity_score = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Study Hours", total_study)
    col2.metric("Total Distraction Hours", total_distraction)
    col3.metric("DSA Questions Solved", total_questions)
    col4.metric("Internship Applications", total_apps)

    st.subheader("Productivity Score")
    st.progress(int(productivity_score))
    st.write(f"Your current productivity score is *{productivity_score}%*")

    st.divider()

    # Study vs Distraction Chart
    if not productivity_df.empty:
        st.subheader("Study Hours vs Distraction Hours")

        productivity_df["entry_date"] = pd.to_datetime(productivity_df["entry_date"])

        daily_data = productivity_df.groupby("entry_date")[
            ["study_hours", "distraction_hours"]
        ].sum()

        st.line_chart(daily_data)

        st.subheader("Main Distractions")

        distraction_count = productivity_df["main_distraction"].value_counts()

        fig, ax = plt.subplots()
        ax.pie(
            distraction_count,
            labels=distraction_count.index,
            autopct="%1.1f%%"
        )
        ax.set_title("Distraction Distribution")
        st.pyplot(fig)
    else:
        st.info("No productivity data added yet.")

    st.divider()

    # DSA Topic Chart
    if not dsa_df.empty:
        st.subheader("DSA Topic-wise Progress")

        topic_data = dsa_df.groupby("topic")["questions_solved"].sum()

        fig, ax = plt.subplots()
        topic_data.plot(kind="bar", ax=ax)
        ax.set_xlabel("Topic")
        ax.set_ylabel("Questions Solved")
        ax.set_title("DSA Progress by Topic")
        st.pyplot(fig)
    else:
        st.info("No DSA progress added yet.")

    st.divider()

    # Internship Status Chart
    if not app_df.empty:
        st.subheader("Internship Application Status")

        status_count = app_df["status"].value_counts()

        fig, ax = plt.subplots()
        status_count.plot(kind="bar", ax=ax)
        ax.set_xlabel("Status")
        ax.set_ylabel("Number of Applications")
        ax.set_title("Application Status Overview")
        st.pyplot(fig)
    else:
        st.info("No internship applications added yet.")

# -----------------------------
# ADD PRODUCTIVITY ENTRY
# -----------------------------
elif menu == "Add Productivity Entry":
    st.header("Add Productivity Entry")

    entry_date = st.date_input("Date", date.today())
    study_hours = st.number_input("Study Hours", min_value=0.0, step=0.5)
    distraction_hours = st.number_input("Distraction Hours", min_value=0.0, step=0.5)

    main_distraction = st.selectbox(
        "Main Distraction",
        [
            "YouTube",
            "Instagram",
            "Netflix",
            "Gaming",
            "WhatsApp",
            "Browsing",
            "Other"
        ]
    )

    if st.button("Save Productivity Entry"):
        c.execute(
            """
            INSERT INTO productivity 
            (entry_date, study_hours, distraction_hours, main_distraction)
            VALUES (?, ?, ?, ?)
            """,
            (str(entry_date), study_hours, distraction_hours, main_distraction)
        )
        conn.commit()
        st.success("Productivity entry saved successfully!")

# -----------------------------
# ADD DSA PROGRESS
# -----------------------------
elif menu == "Add DSA Progress":
    st.header("Add DSA Progress")

    entry_date = st.date_input("Date", date.today())

    topic = st.selectbox(
        "DSA Topic",
        [
            "Arrays",
            "Strings",
            "Linked List",
            "Stack",
            "Queue",
            "Trees",
            "Graphs",
            "Dynamic Programming",
            "Sorting",
            "Searching",
            "Other"
        ]
    )

    questions_solved = st.number_input(
        "Questions Solved",
        min_value=0,
        step=1
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Save DSA Progress"):
        c.execute(
            """
            INSERT INTO dsa_progress
            (entry_date, topic, questions_solved, difficulty)
            VALUES (?, ?, ?, ?)
            """,
            (str(entry_date), topic, questions_solved, difficulty)
        )
        conn.commit()
        st.success("DSA progress saved successfully!")

# -----------------------------
# ADD INTERNSHIP APPLICATION
# -----------------------------
elif menu == "Add Internship Application":
    st.header("Add Internship Application")

    company = st.text_input("Company Name")
    role = st.text_input("Role Applied For")

    status = st.selectbox(
        "Application Status",
        [
            "Applied",
            "Shortlisted",
            "Interview Scheduled",
            "Rejected",
            "Selected"
        ]
    )

    applied_date = st.date_input("Applied Date", date.today())

    if st.button("Save Application"):
        if company.strip() == "" or role.strip() == "":
            st.warning("Please enter company name and role.")
        else:
            c.execute(
                """
                INSERT INTO applications
                (company, role, status, applied_date)
                VALUES (?, ?, ?, ?)
                """,
                (company, role, status, str(applied_date))
            )
            conn.commit()
            st.success("Internship application saved successfully!")

# -----------------------------
# VIEW DATA PAGE
# -----------------------------
elif menu == "View Data":
    st.header("Stored Data")

    productivity_df = load_productivity_data()
    dsa_df = load_dsa_data()
    app_df = load_application_data()

    st.subheader("Productivity Data")
    st.dataframe(productivity_df)

    st.subheader("DSA Progress Data")
    st.dataframe(dsa_df)

    st.subheader("Internship Applications")
    st.dataframe(app_df)

    st.divider()

    if not productivity_df.empty:
        csv = productivity_df.to_csv(index=False)
        st.download_button(
            "Download Productivity Data as CSV",
            csv,
            "productivity_data.csv",
            "text/csv"
        )

    if not dsa_df.empty:
        csv = dsa_df.to_csv(index=False)
        st.download_button(
            "Download DSA Data as CSV",
            csv,
            "dsa_progress.csv",
            "text/csv"
        )

    if not app_df.empty:
        csv = app_df.to_csv(index=False)
        st.download_button(
            "Download Internship Applications as CSV",
            csv,
            "internship_applications.csv",
            "text/csv"
        )