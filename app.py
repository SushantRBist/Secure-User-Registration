import requests  
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient  
import bcrypt  
from flask_mail import Mail, Message  
import secrets  
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature  
from flask_talisman import Talisman  
import bleach 
from datetime import datetime, timedelta  

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '6Lc3rmkrAAAAANTC2qdCKN-oTEC5nltz2wjB4G3S'  # Used to sign tokens and session

# Define secure Content Security Policy
SELF = "'self'"
csp = {
    'default-src': [SELF],
    'style-src': [SELF, "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'font-src': [SELF, 'https://fonts.gstatic.com'],
    'script-src': [SELF, 'https://www.google.com', 'https://www.gstatic.com'],
    'frame-src': ['https://www.google.com', 'https://www.google.com/recaptcha/'],
    'img-src': [SELF, 'https://www.gstatic.com', 'https://www.google.com', 'data:'],
    'connect-src': [SELF, 'https://www.google.com', 'https://www.gstatic.com']
}
Talisman(app, content_security_policy=csp, content_security_policy_nonce_in=['script-src'])

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bistsushant54@gmail.com'
app.config['MAIL_PASSWORD'] = 'vbivndxsezixyfae'
mail = Mail(app)

# MongoDB setup
client = MongoClient("mongodb+srv://bistsushant54:Test123@mydatabase.fy3jiqj.mongodb.net/?retryWrites=true&w=majority&appName=myDatabase")
db = client.user_db
users = db.users

# Token serializer for secure token generation
serializer = URLSafeTimedSerializer(app.secret_key)

# Alert user via email if too many failed login attempts occur
def send_abuse_alert(user, ip):
    now = datetime.utcnow()
    lock_time = user.get('lock_time', now)
    minutes_remaining = 60 - int((now - lock_time).total_seconds() // 60)

    token = serializer.dumps(user['email'], salt='password-reset-salt')
    reset_link = url_for('reset_password', token=token, _external=True)

    msg = Message("Security Alert: Multiple Failed Login Attempts",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user['email']])
    msg.body = f"""Hi {user['first_name']},

We detected 3 failed login attempts for your account `{user['username']}` from IP address {ip}.
As a precaution, your login has been temporarily locked for 1 hour.

⏳ Time remaining: {minutes_remaining} minute(s)

If this wasn't you, you can reset your password here:
{reset_link}

Stay safe,  
– YourApp Security Team
"""
    mail.send(msg)

# Redirect base URL to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Avoid favicon error
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Registration route with email activation and reCAPTCHA
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Sanitize and retrieve form input
        first_name = bleach.clean(request.form.get('first_name'))
        last_name = bleach.clean(request.form.get('last_name'))
        email = bleach.clean(request.form.get('email'))
        username = bleach.clean(request.form.get('username'))
        password = request.form.get('password')

        # Verify reCAPTCHA before proceeding
        recaptcha_response = request.form.get('g-recaptcha-response')
        recaptcha_secret = '6Lc3rmkrAAAAANTC2qdCKN-oTEC5nltz2wjB4G3S'
        payload = {'secret': recaptcha_secret, 'response': recaptcha_response}
        recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()

        if not recaptcha_result.get('success'):
            flash("reCAPTCHA verification failed. Please try again.", 'error')
            return redirect(url_for('register'))

        # Prevent duplicate accounts
        if users.find_one({'username': username}):
            flash("Username already exists!", 'error')
            return redirect(url_for('register'))
        if users.find_one({'email': email}):
            flash("Email already registered!", 'error')
            return redirect(url_for('register'))

        # Hash password and store user as inactive
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        activation_token = secrets.token_urlsafe(16)
        users.insert_one({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'password': hashed_pw,
            'is_active': False,  # 🔒 User must activate via email
            'activation_token': activation_token,
            'password_last_set': datetime.utcnow()
        })

        # Send activation email with unique token
        activation_link = url_for('activate_account', token=activation_token, _external=True)
        msg = Message("Activate Your Account", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Hi {first_name},\n\nPlease click the link below to activate your account:\n\n{activation_link}\n\nThank you!"
        mail.send(msg)

        flash("Registration successful! Please check your email to activate your account.", "info")
        return redirect(url_for('login'))

    return render_template('register.html')

# Route to activate user account from email link
@app.route('/activate/<token>')
def activate_account(token):
    user = users.find_one({'activation_token': token})
    if not user:
        flash("Invalid or expired activation link.", 'error')
        return redirect(url_for('login'))

    users.update_one({'_id': user['_id']}, {
        '$set': {'is_active': True},
        '$unset': {'activation_token': ""}
    })
    flash("Account activated successfully! You can now log in.")
    return redirect(url_for('login'))

# Login route with activation check, lockout, and expiry logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = bleach.clean(request.form['username'])
        password = request.form['password']
        user = users.find_one({'username': username})

        if not user:
            flash("Invalid credentials", 'error')
            return redirect(url_for('login'))

        # Ensure account is activated before allowing login
        if not user.get('is_active'):
            flash("Account not activated. Please check your email.", 'error')
            return redirect(url_for('login'))

        #Check for lockout
        failed_attempts = user.get('failed_attempts', 0)
        locked_until = user.get('locked_until')
        now = datetime.utcnow()

        if locked_until and now < locked_until:
            countdown = int((locked_until - now).total_seconds())
            flash("Account is temporarily locked. Try again later.", 'error')
            return render_template("login.html", countdown=countdown)

        # Successful login
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            users.update_one({'_id': user['_id']}, {
                '$set': {
                    'failed_attempts': 0,
                    'last_failed_time': None,
                    'locked_until': None
                }
            })

            #Warn user if password is near expiry
            password_last_set = user.get('password_last_set', now)
            expires_on = password_last_set + timedelta(days=90)
            days_remaining = (expires_on - now).days

            flash("Logged in successfully!")
            return render_template('welcome.html',
                                   message="Logged in successfully!",
                                   expires_on=expires_on.strftime("%b %d, %Y"),
                                   days_remaining=days_remaining)

        #Handle incorrect password
        failed_attempts += 1
        update_data = {
            'failed_attempts': failed_attempts,
            'last_failed_time': now
        }

        if failed_attempts == 3:
            lockout_time = now + timedelta(hours=1)
            update_data['locked_until'] = lockout_time
            update_data['lock_time'] = now
            send_abuse_alert(user, request.remote_addr)
            flash("Account locked for 1 hour due to multiple failed attempts.", 'error')

        elif failed_attempts == 4:
            lockout_time = now + timedelta(hours=1)
            update_data['locked_until'] = lockout_time
            update_data['failed_attempts'] = 0
            update_data['lock_time'] = now

            token = serializer.dumps(user['email'], salt='password-reset-salt')
            reset_link = url_for('reset_password', token=token, _external=True)

            msg = Message("Reset Your Password",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[user['email']])
            msg.body = f"""Hi {user['first_name']},

You tried logging in again after the lockout but entered the wrong password.

As a precaution, we've disabled login for now and sent you this password reset link:

{reset_link}

This link will expire in 1 hour.

– YourApp Security Team
"""
            msg.html = render_template("email_security_alert.html",
                                       first_name=user['first_name'],
                                       user=user,
                                       reset_link=reset_link)
            mail.send(msg)
            flash("Too many failed attempts. Reset link sent to your email.", 'error')

        users.update_one({'_id': user['_id']}, {'$set': update_data})
        flash("Invalid credentials", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

#Logout clears session
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

#Reset password using token sent to email
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash("Reset link has expired. Please request a new one.")
        return redirect(url_for('forgot'))
    except BadSignature:
        flash("Invalid reset link.")
        return redirect(url_for('forgot'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match.", 'error')
            return redirect(url_for('reset_password', token=token))

        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        users.update_one({'email': email}, {
            '$set': {
                'password': hashed_pw,
                'password_last_set': datetime.utcnow()
            }
        })

        flash("Password reset successfully.", "success")
        return redirect(url_for('login'))

    return render_template('reset.html')

#Forgot password route — sends reset link if email exists
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = bleach.clean(request.form['email'])
        user = users.find_one({'email': email})

        if user:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_link = url_for('reset_password', token=token, _external=True)

            msg = Message("Password Reset Request",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f"""Hi {user['first_name']},

You requested a password reset. Click the link below to reset it:

{reset_link}

This link will expire in 1 hour.

If you didn't request this, you can ignore this message.

– YourApp Security Team
"""
            msg.html = render_template("email_template.html",
                                       first_name=user['first_name'],
                                       reset_link=reset_link)
            mail.send(msg)
            flash("Password reset link has been sent to your email.")
        else:
            flash("Email not found.")
        return redirect(url_for('forgot'))

    return render_template('forgot.html')

#Inject CSP nonce after each response
@app.after_request
def add_nonce(response):
    if 'script-src' in csp:
        nonce = getattr(request, 'csp_nonce', None)
        if nonce:
            response.headers['Content-Security-Policy'] = response.headers.get('Content-Security-Policy', '').replace("'self'", f"'self' 'nonce-{nonce}'")
    return response

#Run app
if __name__ == '__main__':
    app.run(debug=True)
