import io
from openpyxl import Workbook
from flask import Flask, render_template, request, redirect, url_for, Response, send_file, flash
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

@app.route("/export_csv")
def export_csv():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # Important: allows column access by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    conn.close()

    # Make sure there’s at least one row
    if not rows:
        return "No data to export"

    # Build CSV as string
    def generate():
        # Header
        header = rows[0].keys()  # ['id','company','position','status','location','job_link','notes']
        yield ",".join(header) + "\n"

        for row in rows:
            # Convert all values to string and escape commas in text
            yield ",".join([str(row[h]).replace(",", ";") for h in header]) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=applications.csv"}
    )

@app.route("/export_csv/<status>")
def export_csv_filtered(status):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if status == "All":
        cursor.execute("SELECT * FROM applications")
    else:
        cursor.execute("SELECT * FROM applications WHERE status=?", (status,))
    rows = cursor.fetchall()
    conn.close()

    def generate():
        header = rows[0].keys() if rows else ['id','company','position','status','location','job_link','notes']
        yield ','.join(header) + '\n'
        for row in rows:
            yield ','.join([str(row[h]) for h in header]) + '\n'

    return Response(generate(),
                    mimetype='text/csv',
                    headers={"Content-Disposition":f"attachment;filename={status}_applications.csv"})

@app.route("/export_excel")
def export_excel():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No data to export"

    wb = Workbook()
    ws = wb.active
    # Header
    ws.append(list(rows[0].keys()))
    # Data
    for row in rows:
        ws.append([row[h] for h in row.keys()])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="applications.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    app.run(debug=True)
