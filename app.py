from flask import Flask, render_template, request, redirect, flash
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# File to store tasks and job applications
TASKS_FILE = "job_search_tasks.txt"
JOBS_FILE = "job_applications.txt"

# Load tasks from file
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            tasks = file.readlines()
        return [task.strip().split("|") for task in tasks]
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        for task in tasks:
            file.write("|".join(task) + "\n")

# Load job applications from file
def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as file:
            jobs = file.readlines()
        job_list = []
        for job in jobs:
            parts = job.strip().split("|")
            if len(parts) == 6:  # Ensure there are exactly 6 parts
                job_list.append(parts)
        return job_list
    return []

# Save job applications to file
def save_jobs(jobs):
    with open(JOBS_FILE, "w") as file:
        for job in jobs:
            file.write("|".join(job) + "\n")

# Home page
@app.route("/")
def index():
    tasks = load_tasks()
    jobs = load_jobs()
    return render_template("index.html", tasks=tasks, jobs=jobs)

# Add a task
@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.form.get("task")
    category = request.form.get("category")
    if task and category:
        tasks = load_tasks()
        tasks.append(["[ ]", category, task])
        save_tasks(tasks)
        flash("Task added successfully!", "success")
    return redirect("/")

# Mark a task as complete
@app.route("/complete_task/<int:index>")
def complete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index][0] = "[X]"
        save_tasks(tasks)
        flash("Task marked as complete!", "success")
    return redirect("/")

# Remove a task
@app.route("/remove_task/<int:index>")
def remove_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
        flash("Task removed successfully!", "success")
    return redirect("/")

# Add a job application
@app.route("/add_job", methods=["POST"])
def add_job():
    company = request.form.get("company")
    position = request.form.get("position")
    link = request.form.get("link")
    notes = request.form.get("notes")
    if company and position and link:
        date = datetime.now().strftime("%Y-%m-%d")
        jobs = load_jobs()
        jobs.append(["In Progress", company, position, link, date, notes])
        save_jobs(jobs)
        flash("Job application added successfully!", "success")
    return redirect("/")

# Mark job status
@app.route("/mark_job_status/<int:index>", methods=["POST"])
def mark_job_status(index):
    status = request.form.get("status")
    if status:
        jobs = load_jobs()
        if 0 <= index < len(jobs):
            jobs[index][0] = status
            save_jobs(jobs)
            flash("Job status updated successfully!", "success")
    return redirect("/")

# Export data to CSV
@app.route("/export_data")
def export_data():
    jobs = load_jobs()
    file_path = "job_applications_export.csv"
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Status", "Company", "Position", "Link", "Date", "Notes"])
        for job in jobs:
            writer.writerow(job)
    flash(f"Data exported to {file_path}!", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)