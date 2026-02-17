from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "dev-secret-key"


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)  # Get page number from query string
    per_page = 10
    offset = (page - 1) * per_page

    # Get filter & search from query params
    status_filter = request.args.get("status", "All")
    search_query = request.args.get("q", "").strip()
    sort_by = request.args.get("sort_by", "id")  # default sort by id
    sort_dir = request.args.get("sort_dir", "desc")  # default descending

    # Validate sort column & direction to prevent SQL injection
    allowed_columns = ["id", "company", "job_title", "location", "status"]
    allowed_dir = ["asc", "desc"]
    if sort_by not in allowed_columns:
        sort_by = "id"
    if sort_dir not in allowed_dir:
        sort_dir = "desc"

    conn = get_db()

    # Build dynamic WHERE clause
    query = "SELECT * FROM applications WHERE 1=1"
    params = []

    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (company LIKE ? OR job_title LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Get total number of applications
    total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]

     # Add ORDER + LIMIT/OFFSET
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    applications = conn.execute(query, params).fetchall()
    conn.close()

    # Determine if Prev / Next should be active
    has_prev = page > 1
    has_next = offset + per_page < total
    start_record = offset + 1 if total > 0 else 0
    end_record = min(offset + per_page, total)


    return render_template(
        "index.html",
        applications=applications,
        page=page,
        has_prev=has_prev,
        has_next=has_next,
        total=total,
        start_record=start_record,
        end_record=end_record,
        status_filter=status_filter,
        search_query=search_query,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        company = request.form["company"]
        job_title = request.form["job_title"]
        job_link = request.form["job_link"]
        location = request.form["location"]
        applied_date = request.form["applied_date"]
        status = request.form["status"]
        notes = request.form["notes"]

        conn = get_db()
        conn.execute(
            "INSERT INTO applications (company, job_title, job_link, location, applied_date, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (company, job_title, job_link, location, applied_date, status, notes)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM applications WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):
    new_status = request.form["status"]

    conn = get_db()
    conn.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (new_status, id)
    )
    conn.commit()
    conn.close()

    flash("status_updated")
    return redirect(request.referrer)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
            UPDATE applications
            SET company=?, job_title=?, job_link=?, location=?, applied_date=?, status=?, notes=?
            WHERE id=?
        """, (
            request.form["company"],
            request.form["job_title"],
            request.form["job_link"],
            request.form["location"],
            request.form["applied_date"],
            request.form["status"],
            request.form["notes"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    application = conn.execute(
        "SELECT * FROM applications WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    return render_template("edit.html", application=application)

@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools():
    return "", 204

@app.route("/update-notes/<int:id>", methods=["POST"])
def update_notes(id):
    notes = request.form["notes"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applications SET notes = ? WHERE id = ?",
        (notes, id)
    )

    conn.commit()
    conn.close()

    flash("Notes updated successfully!")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
