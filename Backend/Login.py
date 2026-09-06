import hashlib
import re
import mysql.connector
from Database import get_connection


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def validate_email(email):
    if not email:
        return False, "Email is required"

    email = email.strip()

    # Proper email format
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False, "Enter a valid email address"

    return True, ""


def validate_password(password):
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must contain at least 8 characters"

    if len(password) > 128:
        return False, "Password is too long"

    return True, ""


def validate_name(name):
    if not name or not name.strip():
        return False, "Full name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Name must contain at least 2 characters"

    if len(name) > 100:
        return False, "Name is too long"

    if not re.fullmatch(r"[A-Za-z ]+", name):
        return False, "Name can contain only letters and spaces"

    return True, ""


def register_user(name, email, password):

    # Name validation
    valid, message = validate_name(name)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    # Email validation
    valid, message = validate_email(email)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    # Password validation
    valid, message = validate_password(password)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    conn = None
    cursor = None

    try:
        conn = get_connection()

        if conn is None:
            return {
                "success": False,
                "message": "Database connection failed"
            }

        cursor = conn.cursor()

        # Check whether email already exists
        check_query = """
            SELECT user_id
            FROM users
            WHERE email = %s
            LIMIT 1
        """

        cursor.execute(check_query, (email.strip(),))

        if cursor.fetchone():
            return {
                "success": False,
                "message": "Email is already registered"
            }

        password_hash = hash_password(password)

        query = """
            INSERT INTO users
            (full_name, email, password_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (name.strip(), email.strip(), password_hash)
        )

        conn.commit()

        return {
            "success": True,
            "message": "Registration successful"
        }

    except mysql.connector.Error:
        if conn:
            conn.rollback()

        return {
            "success": False,
            "message": "Registration failed"
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def login_user(email, password):

    # Email validation
    valid, message = validate_email(email)

    if not valid:
        return {
            "success": False,
            "message": message,
            "user": None
        }

    # Password validation
    valid, message = validate_password(password)

    if not valid:
        return {
            "success": False,
            "message": message,
            "user": None
        }

    email = email.strip()
    password_hash = hash_password(password)

    conn = None
    cursor = None

    try:
        conn = get_connection()

        if conn is None:
            return {
                "success": False,
                "message": "Database connection failed",
                "user": None
            }

        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT user_id, full_name, email
            FROM users
            WHERE email = %s
              AND password_hash = %s
            LIMIT 1
        """

        cursor.execute(
            query,
            (email, password_hash)
        )

        user = cursor.fetchone()

        if user:
            return {
                "success": True,
                "message": "Login successful",
                "user": user
            }

        return {
            "success": False,
            "message": "Invalid email or password",
            "user": None
        }

    except mysql.connector.Error:
        return {
            "success": False,
            "message": "Login failed",
            "user": None
        }

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()