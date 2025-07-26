from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from settings import ADMIN_USERNAME, ADMIN_PASSWORD
from models import OTP, db
from datetime import datetime, timedelta, timezone
import random
from models import OTP, db
from datetime import datetime, timezone
from emailing import send_email 

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in ADMIN_USERNAME.split(',') and password in ADMIN_PASSWORD.split(','):
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            otp = OTP(otp=otp_code, expires_at=expires_at)
            db.session.add(otp)
            db.session.commit()
            session['pending_admin'] = True
            session['otp_id'] = otp.id
            send_email(
                subject="INFINITY Bot Admin Login OTP",
                recipient=username,
                body=f"""
                <html>
                <head>
                  <style>
                    body {{
                      background: #f5f7fa;
                      font-family: 'Segoe UI', Arial, sans-serif;
                      color: #222;
                      margin: 0;
                      padding: 0;
                    }}
                    .container {{
                      max-width: 420px;
                      margin: 40px auto;
                      background: #fff;
                      border-radius: 12px;
                      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                      padding: 32px 28px;
                    }}
                    .logo {{
                      text-align: center;
                      margin-bottom: 24px;
                    }}
                    .logo span {{
                      font-size: 2.2em;
                      font-weight: bold;
                      color: #4f8cff;
                      letter-spacing: 2px;
                    }}
                    .otp-title {{
                      font-size: 1.3em;
                      font-weight: 600;
                      text-align: center;
                      margin-bottom: 18px;
                      color: #222;
                    }}
                    .otp-code {{
                      display: block;
                      width: fit-content;
                      margin: 0 auto 18px auto;
                      font-size: 2.1em;
                      letter-spacing: 10px;
                      font-weight: bold;
                      background: #f0f6ff;
                      color: #4f8cff;
                      border-radius: 8px;
                      padding: 12px 28px;
                      border: 1px dashed #4f8cff;
                    }}
                    .desc {{
                      text-align: center;
                      color: #555;
                      font-size: 1em;
                      margin-bottom: 18px;
                    }}
                    .footer {{
                      text-align: center;
                      color: #aaa;
                      font-size: 0.95em;
                      margin-top: 32px;
                    }}
                  </style>
                </head>
                <body>
                  <div class="container">
                    <div class="logo">
                      <span>INFINITY</span>
                    </div>
                    <div class="otp-title">Admin Login Verification</div>
                    <div class="desc">
                      Please use the following OTP code to complete your admin login.<br>
                      This code is valid for <b>5 minutes</b>.
                    </div>
                    <div class="otp-code">{otp_code}</div>
                    <div class="desc">
                      If you did not request this code, please ignore this email.
                    </div>
                    <div class="footer">
                      &copy; {datetime.now().year} INFINITY Bot. All rights reserved.
                    </div>
                  </div>
                </body>
                </html>
                """
            )
            return redirect(url_for('admin.otp_verify'))
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/otp-verify', methods=['GET', 'POST'])
def otp_verify():

    otp_id = session.get('otp_id')
    if not otp_id:
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('admin.login'))

    otp_obj = OTP.query.get(otp_id)
    if not otp_obj:
        flash('OTP not found. Please login again.', 'error')
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        otp_input = request.form['otp']
        if otp_obj.otp == otp_input and otp_obj.is_valid():
            session.pop('pending_admin', None)
            session.pop('otp_id', None)
            session['admin_logged_in'] = True
            db.session.delete(otp_obj)
            db.session.commit()
            return redirect(url_for('home.dashboard'))
        else:
            flash('Invalid or expired OTP.', 'error')
    return render_template('admin_otp_verify.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.login'))
