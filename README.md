# SureSight Complete Website + Booking System + Admin Dashboard

A runnable Flask + SQLite project built around the supplied SureSight Home Inspection branding and contact/rate-card details. It includes a responsive public website, a booking form that stores enquiries in SQLite, an admin dashboard, status updates, internal notes, CSV export, and an installable Progressive Web App (PWA) experience for Android/iPhone.

## Requirements
- Python 3.10+ (Python 3.11 or 3.12 recommended)
- Internet access for the first-time Flask install
- A modern browser

## Run on Windows
1. Extract the ZIP to a folder such as `C:\SureSight`.
2. Open that folder in File Explorer.
3. Double-click `run_windows.bat`.
4. When startup completes, visit `http://127.0.0.1:5000`.

If Windows blocks the batch file, open Command Prompt in the project folder and run:
```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
set SURESIGHT_SECRET_KEY=use-a-long-random-secret-here
set SURESIGHT_ADMIN_PASSWORD=choose-a-strong-password-here
python app.py
```

## Run on macOS / Linux
```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```
Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SURESIGHT_SECRET_KEY='use-a-long-random-secret-here'
export SURESIGHT_ADMIN_PASSWORD='choose-a-strong-password-here'
python app.py
```

## Admin dashboard
- URL: `http://127.0.0.1:5000/admin/login`
- Default username: `admin`
- Default password: `ChangeMe-Now-123!`

**Change the default password and secret key before deployment.** These values are read when the app initializes. If the database has already been created, changing the environment password alone does not overwrite the stored password hash. For a fresh local reset, stop the server and delete `suresight.db`, then restart with the new environment values. This deletes local bookings too, so export any data you need first.

The dashboard supports:
- Viewing all booking requests
- Searching by customer name, phone, location, or booking ID
- Filtering by status
- Updating status: New, Contacted, Inspection Scheduled, Completed, Cancelled
- Adding internal notes
- Exporting a booking as CSV

## Public booking flow
1. Customer completes the form on the home page.
2. The request is saved to `suresight.db`.
3. A booking number is shown.
4. Customer can open WhatsApp with the request details pre-filled to contact SureSight.
5. SureSight staff manage the enquiry in the admin dashboard.

The website does not automatically send SMS, email, WhatsApp messages, payments, or push notifications. The customer must tap the WhatsApp button and send the prepared message. The booking is a request, not a confirmed appointment.

## Android app
This project is a Progressive Web App. For local development, use `http://127.0.0.1:5000`; for installation on an actual Android phone, deploy the app to an HTTPS domain, open it in Chrome, and choose **Install app** / **Add to Home screen** from the browser menu. A PWA gives customers an app-like icon and full-screen experience without maintaining a separate native Android codebase.

### Optional native Android wrapper
The `android-wrapper` folder contains notes for a future Capacitor wrapper. A signed APK/AAB is not included because it requires Android Studio/SDK setup, application signing, and a deployed backend URL. See `android-wrapper/README.md`.

## Deploying publicly
This is a starter intended to be run and tested first. Before public production use:
- Set a strong `SURESIGHT_SECRET_KEY` and `SURESIGHT_ADMIN_PASSWORD`.
- Use HTTPS.
- Use a production WSGI server such as Waitress on Windows or Gunicorn on Linux; do not use Flask's development server for production.
- Configure a persistent disk/volume for `suresight.db`, plus backups.
- Add CSRF protection for public booking and rate limiting on login and booking endpoints.
- Consider role-based staff accounts, email/SMS notifications, report uploads, privacy notice/consent, and data-retention rules.
- Verify rates, inspection scope, contact details, and service-area coverage with SureSight before launch.

## Project layout
- `app.py` — Flask routes, SQLite setup, login, booking storage, dashboard and CSV export
- `templates/` — public website and admin pages
- `static/styles.css` — responsive styling
- `static/app.js` — navigation and PWA registration
- `static/sw.js` — basic cache/offline support
- `static/icons/icon.svg` — app icon
- `suresight.db` — created automatically on first run
