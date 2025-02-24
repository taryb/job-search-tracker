import sys
import os
import shutil
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, 
    QLabel, QMessageBox, QInputDialog, QDateEdit, QCheckBox, QTextEdit, QFileDialog, QTabWidget, QDialog
)
from PyQt5.QtCore import QDateTime

# SQLite database file
DATABASE_FILE = "job_search.db"

# Create a folder for documents if it doesn't exist
DOCUMENTS_FOLDER = "JobSearchDocuments"
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Create jobs table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            position TEXT NOT NULL,
            link TEXT NOT NULL,
            date TEXT NOT NULL,
            cover_letter TEXT NOT NULL,
            notes TEXT NOT NULL,
            folder TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Load jobs from SQLite database
def load_jobs():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Save a job to SQLite database
def save_job(status, position, link, date, cover_letter, notes, folder):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (status, position, link, date, cover_letter, notes, folder)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (status, position, link, date, cover_letter, notes, folder))
    conn.commit()
    conn.close()

# Update a job in SQLite database
def update_job(job_id, status, position, link, date, cover_letter, notes, folder):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jobs
        SET status = ?, position = ?, link = ?, date = ?, cover_letter = ?, notes = ?, folder = ?
        WHERE id = ?
    ''', (status, position, link, date, cover_letter, notes, folder, job_id))
    conn.commit()
    conn.close()

# Delete a job from SQLite database
def delete_job(job_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

# Window to view job details
class ViewJobWindow(QDialog):
    def __init__(self, job_details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Job Details")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(self)

        # Display job details
        self.status_label = QLabel(f"Status: {job_details[1]}")
        layout.addWidget(self.status_label)

        self.position_label = QLabel(f"Position: {job_details[2]}")
        layout.addWidget(self.position_label)

        self.link_label = QLabel(f"Link: {job_details[3]}")
        layout.addWidget(self.link_label)

        self.date_label = QLabel(f"Date: {job_details[4]}")
        layout.addWidget(self.date_label)

        self.cover_letter_label = QLabel(f"Cover Letter Submitted: {job_details[5]}")
        layout.addWidget(self.cover_letter_label)

        self.notes_label = QLabel(f"Notes: {job_details[6]}")
        layout.addWidget(self.notes_label)

        self.folder_label = QLabel(f"Documents Folder: {job_details[7]}")
        layout.addWidget(self.folder_label)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

# Main application window
class JobSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Search Tracker")
        self.setGeometry(100, 100, 800, 600)

        # Initialize database
        initialize_database()

        # Load jobs
        self.jobs = load_jobs()

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Create tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Job application tab
        self.job_tab = QWidget()
        self.tabs.addTab(self.job_tab, "Job Applications")
        self.job_layout = QVBoxLayout(self.job_tab)

        # Add widgets to the job tab
        self.dashboard_label = QLabel(self.job_tab)
        self.job_layout.addWidget(self.dashboard_label)
        self.update_dashboard()

        self.job_position_input = QLineEdit(self.job_tab)
        self.job_position_input.setPlaceholderText("Enter job position (e.g., 'Optics Engineer')")
        self.job_layout.addWidget(self.job_position_input)

        self.job_link_input = QLineEdit(self.job_tab)
        self.job_link_input.setPlaceholderText("Enter job link (e.g., LinkedIn job URL)")
        self.job_layout.addWidget(self.job_link_input)

        self.job_date_input = QDateEdit(self.job_tab)
        self.job_date_input.setCalendarPopup(True)
        self.job_date_input.setDate(QDateTime.currentDateTime().date())
        self.job_layout.addWidget(QLabel("Application Date:"))
        self.job_layout.addWidget(self.job_date_input)

        self.cover_letter_checkbox = QCheckBox("Cover Letter Submitted", self.job_tab)
        self.job_layout.addWidget(self.cover_letter_checkbox)

        self.notes_input = QTextEdit(self.job_tab)
        self.notes_input.setPlaceholderText("Add notes about this job application...")
        self.job_layout.addWidget(self.notes_input)

        self.add_job_button = QPushButton("Add Job Application", self.job_tab)
        self.add_job_button.clicked.connect(self.add_job)
        self.job_layout.addWidget(self.add_job_button)

        self.job_list = QListWidget(self.job_tab)
        self.job_layout.addWidget(self.job_list)
        self.update_job_list()

        self.mark_job_status_button = QPushButton("Mark Job Status", self.job_tab)
        self.mark_job_status_button.clicked.connect(self.mark_job_status)
        self.job_layout.addWidget(self.mark_job_status_button)

        self.remove_job_button = QPushButton("Remove Job", self.job_tab)
        self.remove_job_button.clicked.connect(self.remove_job)
        self.job_layout.addWidget(self.remove_job_button)

        self.upload_button = QPushButton("Upload Resume/Cover Letter", self.job_tab)
        self.upload_button.clicked.connect(self.upload_document)
        self.job_layout.addWidget(self.upload_button)

        self.view_documents_button = QPushButton("View Documents", self.job_tab)
        self.view_documents_button.clicked.connect(self.view_documents)
        self.job_layout.addWidget(self.view_documents_button)

        self.view_job_button = QPushButton("View Job", self.job_tab)
        self.view_job_button.clicked.connect(self.view_job)
        self.job_layout.addWidget(self.view_job_button)

    # Update dashboard
    def update_dashboard(self):
        total_jobs = len(self.jobs)
        in_progress = sum(1 for job in self.jobs if job[1] == "In Progress")
        rejected = sum(1 for job in self.jobs if job[1] == "Rejected")
        accepted = sum(1 for job in self.jobs if job[1] == "Accepted")

        dashboard_text = (
            f"Total Applications: {total_jobs}\n"
            f"In Progress: {in_progress}\n"
            f"Rejected: {rejected}\n"
            f"Accepted: {accepted}\n"
        )
        self.dashboard_label.setText(dashboard_text)

    # Update job list
    def update_job_list(self):
        self.job_list.clear()
        for job in self.jobs:
            status = job[1]
            position = job[2]
            date = job[4]
            cover_letter = "Yes" if job[5] == "True" else "No"
            notes = job[6]
            self.job_list.addItem(f"{status} - {position} - {date} - Cover Letter: {cover_letter}\nNotes: {notes}")

    # Add a job application
    def add_job(self):
        job_position = self.job_position_input.text().strip()
        job_link = self.job_link_input.text().strip()
        job_date = self.job_date_input.date().toString("yyyy-MM-dd")
        cover_letter_submitted = str(self.cover_letter_checkbox.isChecked())
        notes = self.notes_input.toPlainText().strip()
        if job_position and job_link:
            # Create a unique folder name using job position and timestamp
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            job_folder = os.path.join(DOCUMENTS_FOLDER, f"{job_position.replace('/', '_')}_{timestamp}")
            if not os.path.exists(job_folder):
                os.makedirs(job_folder)

            # Save the job to the database
            save_job("In Progress", job_position, job_link, job_date, cover_letter_submitted, notes, job_folder)
            self.jobs = load_jobs()  # Reload jobs from the database
            self.job_position_input.clear()
            self.job_link_input.clear()
            self.cover_letter_checkbox.setChecked(False)
            self.notes_input.clear()
            self.update_job_list()
            self.update_dashboard()

    # Mark job status
    def mark_job_status(self):
        selected_job = self.job_list.currentRow()
        if selected_job >= 0:
            job_id = self.jobs[selected_job][0]
            status, ok = QInputDialog.getItem(self, "Mark Job Status", "Select status:", ["In Progress", "Rejected", "Accepted"], 0, False)
            if ok and status:
                update_job(job_id, status, self.jobs[selected_job][2], self.jobs[selected_job][3], self.jobs[selected_job][4], self.jobs[selected_job][5], self.jobs[selected_job][6], self.jobs[selected_job][7])
                self.jobs = load_jobs()  # Reload jobs from the database
                self.update_job_list()
                self.update_dashboard()

    # Remove a job application
    def remove_job(self):
        selected_job = self.job_list.currentRow()
        if selected_job >= 0:
            job_id = self.jobs[selected_job][0]
            job_folder = self.jobs[selected_job][7]  # Get the folder name
            if os.path.exists(job_folder):
                shutil.rmtree(job_folder)  # Delete the folder
            delete_job(job_id)
            self.jobs = load_jobs()  # Reload jobs from the database
            self.update_job_list()
            self.update_dashboard()

    # Upload document
    def upload_document(self):
        selected_job = self.job_list.currentRow()
        if selected_job >= 0:
            job_folder = self.jobs[selected_job][7]  # Get the folder name from the job data
            if not os.path.exists(job_folder):
                os.makedirs(job_folder)

            file_path, _ = QFileDialog.getOpenFileName(self, "Upload Document", "", "PDF Files (*.pdf);;Word Files (*.docx)")
            if file_path:
                file_name = os.path.basename(file_path)
                destination_path = os.path.join(job_folder, file_name)
                shutil.copy(file_path, destination_path)
                QMessageBox.information(self, "Success", f"Document '{file_name}' uploaded successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please select a job first.")

    # View documents
    def view_documents(self):
        selected_job = self.job_list.currentRow()
        if selected_job >= 0:
            job_folder = self.jobs[selected_job][7]  # Get the folder name from the job data
            if os.path.exists(job_folder):
                if sys.platform == "win32":
                    os.startfile(job_folder)
                elif sys.platform == "darwin":
                    subprocess.run(["open", job_folder])
                else:
                    subprocess.run(["xdg-open", job_folder])
            else:
                QMessageBox.warning(self, "Error", "No documents uploaded for this job.")
        else:
            QMessageBox.warning(self, "Error", "Please select a job first.")

    # View job details in a new window
    def view_job(self):
        selected_job = self.job_list.currentRow()
        if selected_job >= 0:
            job_details = self.jobs[selected_job]
            self.view_job_window = ViewJobWindow(job_details, self)
            self.view_job_window.exec_()
        else:
            QMessageBox.warning(self, "Error", "Please select a job first.")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobSearchApp()
    window.show()
    sys.exit(app.exec_())