import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("SURESIGHT_DB", os.path.join(BASE_DIR, "suresight.db"))
ADMIN_USERNAME = os.environ.get("SURESIGHT_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("SURESIGHT_ADMIN_PASSWORD", "ChangeMe-Now-123!")
SECRET_KEY = os.environ.get("SURESIGHT_SECRET_KEY", "dev-only-change-this-secret-key")
WHATSAPP_NUMBER = "917058469071"
CONTACT_EMAIL = "suresight0687@gmail.com"
CONTACTS = [
    {"name": "Er. Omkar Narnale", "phone": "+91 70584 69071", "tel": "+917058469071"},
    {"name": "Er. Sambodhi Dhutraj", "phone": "+91 74208 59592", "tel": "+917420859592"},
]
SERVICES = [
    "Pre-possession inspection",
    "Snag list preparation",
    "Plumbing & electrical inspection",
    "Tile, civil & finishing check",
    "Waterproofing inspection",
    "Complete home inspection",
]
PRICING = [
    {"type": "1 BHK", "details": "1 bedroom + hall + kitchen", "price": "₹3,000 – ₹6,500", "area": "600–1,000 sq. ft."},
    {"type": "2 & 3 BHK", "details": "2 / 3 bedrooms + hall + kitchen", "price": "₹4,500 – ₹9,500", "area": "1,000–2,000 sq. ft."},
    {"type": "4 & 5 BHK", "details": "4 / 5 bedrooms + hall + kitchen", "price": "₹7,500 – ₹15,500", "area": "2,000+ sq. ft."},
]

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                bhk TEXT NOT NULL,
                location TEXT NOT NULL,
                area TEXT,
                preferred_date TEXT,
                service TEXT NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'New',
                admin_notes TEXT DEFAULT ''
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        row = db.execute("SELECT username FROM admin_users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
        if not row:
            db.execute(
                "INSERT INTO admin_users(username, password_hash) VALUES (?, ?)",
                (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD))
            )


init_db()


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_user"):
            return redirect(url_for("admin_login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.context_processor
def shared_context():
    return {"services": SERVICES, "pricing": PRICING, "contacts": CONTACTS, "contact_email": CONTACT_EMAIL, "current_year": datetime.now().year}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/manifest.json")
def manifest():
    return jsonify({
        "name": "SureSight Home Inspection",
        "short_name": "SureSight",
        "description": "Professional home quality inspection and booking",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#07558e",
        "icons": [{"src": "/static/icons/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
    })


@app.get("/sw.js")
def service_worker():
    return app.send_static_file("sw.js")


@app.post("/book")
def book():
    fields = {
        "customer_name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "bhk": request.form.get("bhk", "").strip(),
        "location": request.form.get("location", "").strip(),
        "area": request.form.get("area", "").strip(),
        "preferred_date": request.form.get("date", "").strip(),
        "service": request.form.get("service", "").strip(),
        "notes": request.form.get("notes", "").strip(),
    }
    if not fields["customer_name"] or not fields["phone"] or not fields["bhk"] or not fields["location"]:
        flash("Please complete your name, phone, apartment type, and property location.", "error")
        return redirect(url_for("home") + "#contact")
    if fields["service"] not in SERVICES:
        fields["service"] = "Complete home inspection"
    if len(fields["customer_name"]) > 120 or len(fields["phone"]) > 40 or len(fields["location"]) > 250:
        flash("One or more fields are too long. Please check your details.", "error")
        return redirect(url_for("home") + "#contact")
    with connect_db() as db:
        cur = db.execute("""
            INSERT INTO bookings (created_at, customer_name, phone, bhk, location, area, preferred_date, service, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fields["customer_name"], fields["phone"],
              fields["bhk"], fields["location"], fields["area"], fields["preferred_date"],
              fields["service"], fields["notes"]))
        booking_id = cur.lastrowid
    message = (
        f"Hello SureSight team, I submitted booking request #{booking_id}.\\n"
        f"Name: {fields['customer_name']}\\nPhone: {fields['phone']}\\nApartment: {fields['bhk']}\\n"
        f"Location: {fields['location']}\\nArea: {fields['area'] or 'Not specified'} sq. ft.\\n"
        f"Preferred date: {fields['preferred_date'] or 'Flexible'}\\nService: {fields['service']}\\n"
        f"Details: {fields['notes'] or 'None'}\\nPlease confirm availability and final charges."
    )
    return render_template("booking_success.html", booking_id=booking_id,
                           whatsapp_url=f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(message)}")


@app.get("/admin/login")
def admin_login():
    if session.get("admin_user"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")


@app.post("/admin/login")
def admin_login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    with connect_db() as db:
        user = db.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session["admin_user"] = username
        session["csrf_token"] = secrets.token_urlsafe(24)
        return redirect(request.args.get("next") or url_for("admin_dashboard"))
    flash("Invalid username or password.", "error")
    return redirect(url_for("admin_login"))


@app.post("/admin/logout")
@admin_required
def admin_logout():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin_dashboard():
    status = request.args.get("status", "").strip()
    search = request.args.get("q", "").strip()
    allowed_statuses = ["New", "Contacted", "Inspection Scheduled", "Completed", "Cancelled"]
    clauses, params = [], []
    if status in allowed_statuses:
        clauses.append("status = ?")
        params.append(status)
    if search:
        clauses.append("(customer_name LIKE ? OR phone LIKE ? OR location LIKE ? OR CAST(id AS TEXT) = ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", search.lstrip("#")])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with connect_db() as db:
        bookings = db.execute("SELECT * FROM bookings" + where + " ORDER BY id DESC", params).fetchall()
        counts = {s: db.execute("SELECT COUNT(*) FROM bookings WHERE status = ?", (s,)).fetchone()[0] for s in allowed_statuses}
        total = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    return render_template("admin_dashboard.html", bookings=bookings, counts=counts, total=total,
                           current_status=status, search=search, allowed_statuses=allowed_statuses,
                           csrf_token=session.get("csrf_token", ""))


@app.post("/admin/booking/<int:booking_id>/update")
@admin_required
def update_booking(booking_id):
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)
    status = request.form.get("status", "New")
    allowed = ["New", "Contacted", "Inspection Scheduled", "Completed", "Cancelled"]
    if status not in allowed:
        abort(400)
    admin_notes = request.form.get("admin_notes", "").strip()[:2000]
    with connect_db() as db:
        cur = db.execute("UPDATE bookings SET status = ?, admin_notes = ? WHERE id = ?",
                         (status, admin_notes, booking_id))
    if cur.rowcount == 0:
        abort(404)
    flash(f"Booking #{booking_id} updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.get("/admin/booking/<int:booking_id>/export")
@admin_required
def export_booking(booking_id):
    with connect_db() as db:
        booking = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        abort(404)
    from flask import make_response
    import csv
    from io import StringIO
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(booking.keys())
    writer.writerow([booking[k] for k in booking.keys()])
    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=suresight-booking-{booking_id}.csv"
    return response


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "SureSight Home Inspection"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False
    )