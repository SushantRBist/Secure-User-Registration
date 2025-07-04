# Secure User Registration Portal

A secure user authentication portal built with Flask, MongoDB, and Flask-Mail. Features include registration with email activation, login with account lockout and password expiry, password reset via email, and Google reCAPTCHA protection.

## Features

- User registration with email activation link
- Secure login with account lockout after multiple failed attempts
- Password reset via email with expiring token
- Password expiry notification (90 days)
- Google reCAPTCHA integration to prevent bots
- Secure Content Security Policy (CSP) with nonce
- Password strength validation (frontend, not shown in this code)
- MongoDB for user data storage
- Email notifications for security alerts and password resets

## Technologies Used

- Python 3
- Flask
- Flask-Mail
- Flask-Talisman (CSP)
- PyMongo (MongoDB)
- bcrypt (password hashing)
- itsdangerous (token generation)
- Google reCAPTCHA

## Setup Instructions

1. **Clone the repository**

   ```sh
   git clone https://github.com/SushantRBist/Secure-User-Registration.git
   cd Secure-User-Registration
   ```

2. **Install dependencies**

   ```sh
   pip install -r requirement.txt
   ```

3. **Configure environment variables**

   - Update `MAIL_USERNAME` and `MAIL_PASSWORD` in `app.py` with your Gmail credentials or use environment variables for security.
   - Update MongoDB connection string in `app.py` if needed.

4. **Run the application**

   ```sh
   python app.py
   ```

5. **Access the portal**

   Open [http://localhost:5000](http://localhost:5000) in your browser.

## File Structure

- `app.py` — Main Flask application
- `static/` — CSS, JS, and images
- `templates/` — HTML templates for all pages and emails
- `requirement.txt` — Python dependencies

## Security Notes

- Do not commit real credentials to version control.
- For production, use environment variables for secrets and email credentials.
- Ensure MongoDB is secured and not publicly accessible.

## License

MIT License

---

**Developed by SushantRBist**
