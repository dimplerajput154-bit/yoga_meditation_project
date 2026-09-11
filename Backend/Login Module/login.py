import os
import sys
from pathlib import Path

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Database_Module import connection


# =========================================================
# Flask Application
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path="/static"
)

CORS(
    app,
    supports_credentials=True
)

app.config["SECRET_KEY"] = "wellness_secret_key_12345"


# =========================================================
# Login Manager
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)


# =========================================================
# User Class
# =========================================================

class User(UserMixin):

    def __init__(self, user_id, full_name, email):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email

    def get_id(self):
        return str(self.user_id)


# =========================================================
# Load User
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    conn = None
    cursor = None

    try:

        conn = connection()

        if conn is None:
            return None

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, full_name, email
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user:

            return User(
                user["user_id"],
                user["full_name"],
                user["email"]
            )

        return None

    except Exception as e:

        print("Load User Error:", e)

        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# Home / Test
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return render_template("login.html")


# =========================================================
# Registration
# =========================================================

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not full_name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "Full name, email and password are required."
        }), 400

    if len(full_name) > 100 or len(email) > 120:
        return jsonify({
            "status": "error",
            "message": "Name or email is too long."
        }), 400

    if len(password) < 6:
        return jsonify({
            "status": "error",
            "message": "Password must be at least 6 characters."
        }), 400

    conn = None
    cursor = None
    try:
        conn = connection()
        if conn is None:
            return jsonify({
                "status": "error",
                "message": "Database connection failed."
            }), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "An account with this email already exists."
            }), 409

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, generate_password_hash(password))
        )
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Registration successful."
        }), 201
    except Exception as error:
        if conn:
            conn.rollback()
        print("Registration Error:", error)
        return jsonify({
            "status": "error",
            "message": "Something went wrong during registration."
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# Login
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # GET request for testing

    if request.method == "GET":

        return jsonify({
            "status": "success",
            "message": "Login API is working.",
            "method": "POST",
            "required_fields": [
                "email",
                "password"
            ]
        })


    # Get JSON data

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required."
        }), 400


    email = data.get("email")
    password = data.get("password")


    # Validate input

    if not email or not password:

        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400


    conn = None
    cursor = None

    try:

        # Connect to existing ai_wellness_db

        conn = connection()

        if conn is None:

            return jsonify({
                "status": "error",
                "message": "Database connection failed."
            }), 500


        cursor = conn.cursor(dictionary=True)


        # Find user

        cursor.execute(
            """
            SELECT user_id, full_name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()


        # User not found

        if user is None:

            return jsonify({
                "status": "error",
                "message": "User not found. Please register first."
            }), 404


        # Check password

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            return jsonify({
                "status": "error",
                "message": "Invalid email or password."
            }), 401


        # Create Flask login session

        logged_user = User(
            user["user_id"],
            user["full_name"],
            user["email"]
        )

        login_user(logged_user)


        return jsonify({

            "status": "success",

            "message": "Login successful.",

            "user": {

                "id": user["user_id"],

                "name": user["full_name"],

                "email": user["email"]

            }

        })


    except Exception as e:

        print("Login Error:", e)

        return jsonify({
            "status": "error",
            "message": "Something went wrong during login."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# Check Login
# =========================================================

@app.route("/check-login", methods=["GET"])
def check_login():

    if current_user.is_authenticated:

        return jsonify({

            "status": "success",

            "logged_in": True,

            "user": {

                "id": current_user.user_id,

                "name": current_user.full_name,

                "email": current_user.email

            }

        })


    return jsonify({

        "status": "success",

        "logged_in": False,

        "message": "User is not logged in."

    })


# =========================================================
# Logout
# =========================================================

@app.route("/logout", methods=["GET", "POST"])
def logout():

    if current_user.is_authenticated:

        logout_user()

        return jsonify({

            "status": "success",

            "message": "Logout successful."

        })


    return jsonify({

        "status": "success",

        "message": "No active login session."

    })


# =========================================================
# Run Application
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print("          AI WELLNESS LOGIN SERVER")

    print("=" * 60)

    print("Server:")
    print("http://127.0.0.1:5001")

    print()

    print("Login:")
    print("http://127.0.0.1:5001/login")

    print()

    print("Check Login:")
    print("http://127.0.0.1:5001/check-login")

    print()

    print("Logout:")
    print("http://127.0.0.1:5001/logout")

    print("=" * 60)

    app.run(
        debug=True,
        port=5001
    )
